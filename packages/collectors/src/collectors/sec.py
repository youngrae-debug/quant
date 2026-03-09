from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import Any

import httpx
from sqlalchemy import text

from .config import settings
from .db import engine
from .logging import get_logger

logger = get_logger(__name__)


def _normalize_cik(value: Any) -> str | None:
    if value is None:
        return None
    as_str = str(value).strip()
    if not as_str:
        return None
    digits = ''.join(ch for ch in as_str if ch.isdigit())
    return digits.zfill(10) if digits else None


def _normalize_sic(value: Any) -> str | None:
    if value is None:
        return None
    as_str = str(value).strip()
    return as_str or None


def _fetch_json(client: httpx.Client, url: str) -> dict[str, Any]:
    for attempt in range(1, 6):
        response = client.get(url)
        if response.status_code == 429:
            sleep_for = settings.rate_limit_sleep_seconds * attempt
            logger.warning('Rate limited on %s; sleeping %.2fs', url, sleep_for)
            time.sleep(sleep_for)
            continue
        response.raise_for_status()
        return response.json()
    raise RuntimeError(f'Failed after retries: {url}')


def sync_sec_symbols(enrich_sic: bool = True, sic_enrichment_limit: int = 200) -> int:
    headers = {'User-Agent': settings.sec_user_agent}
    client = httpx.Client(timeout=settings.request_timeout_seconds, headers=headers)

    ticker_url = f'{settings.sec_base_url}/files/company_tickers_exchange.json'
    payload = _fetch_json(client, ticker_url)

    rows = payload.get('data', [])
    if not rows:
        logger.warning('SEC ticker payload empty from %s', ticker_url)
        return 0

    upsert_sql = text(
        """
        INSERT INTO symbols (ticker, cik, exchange, name, is_active, updated_at)
        VALUES (:ticker, :cik, :exchange, :name, true, now())
        ON CONFLICT (ticker)
        DO UPDATE SET
            cik = COALESCE(EXCLUDED.cik, symbols.cik),
            exchange = COALESCE(EXCLUDED.exchange, symbols.exchange),
            name = COALESCE(EXCLUDED.name, symbols.name),
            is_active = true,
            updated_at = now()
        """
    )

    synced = 0
    with engine.begin() as conn:
        for row in rows:
            try:
                ticker = str(row[2]).strip().upper()
                if not ticker:
                    continue
                conn.execute(
                    upsert_sql,
                    {
                        'ticker': ticker,
                        'cik': _normalize_cik(row[0]),
                        'exchange': str(row[1]).strip() or None,
                        'name': str(row[3]).strip() or None,
                    },
                )
                synced += 1
            except Exception as exc:  # noqa: BLE001
                logger.exception('Failed syncing SEC ticker row=%s: %s', row, exc)

    if enrich_sic:
        _enrich_sic_from_submissions(client, limit=sic_enrichment_limit)

    logger.info('SEC symbol sync complete: %s records processed', synced)
    return synced


def _enrich_sic_from_submissions(client: httpx.Client, limit: int = 200) -> None:
    select_sql = text(
        """
        SELECT id, cik
        FROM symbols
        WHERE cik IS NOT NULL
          AND (sic IS NULL OR sic = '')
        ORDER BY id
        LIMIT :limit
        """
    )
    update_sql = text('UPDATE symbols SET sic = :sic, updated_at = now() WHERE id = :id')

    with engine.begin() as conn:
        symbols = conn.execute(select_sql, {'limit': limit}).mappings().all()
        for symbol in symbols:
            cik = symbol['cik']
            if not cik:
                continue
            url = f'{settings.sec_base_url}/submissions/CIK{cik}.json'
            try:
                payload = _fetch_json(client, url)
                sic = _normalize_sic(payload.get('sic'))
                if sic:
                    conn.execute(update_sql, {'sic': sic, 'id': symbol['id']})
            except Exception as exc:  # noqa: BLE001
                logger.exception('Failed SIC enrichment cik=%s: %s', cik, exc)


def sync_sec_filings(max_symbols: int = 100) -> int:
    """Idempotent filing/companyfacts sync into filing_facts via upsert."""
    headers = {'User-Agent': settings.sec_user_agent}
    client = httpx.Client(timeout=settings.request_timeout_seconds, headers=headers)

    symbols_sql = text(
        """
        SELECT id, ticker, cik
        FROM symbols
        WHERE is_active = true AND cik IS NOT NULL
        ORDER BY id
        LIMIT :max_symbols
        """
    )
    upsert_sql = text(
        """
        INSERT INTO filing_facts (
            symbol_id, filing_date, period_end_date, revenue_ttm, net_income_ttm, eps_ttm, source, raw_payload, created_at
        ) VALUES (
            :symbol_id, :filing_date, :period_end_date, :revenue_ttm, :net_income_ttm, :eps_ttm, 'sec-companyfacts', :raw_payload::jsonb, now()
        )
        ON CONFLICT (symbol_id, filing_date, period_end_date)
        DO UPDATE SET
            revenue_ttm = COALESCE(EXCLUDED.revenue_ttm, filing_facts.revenue_ttm),
            net_income_ttm = COALESCE(EXCLUDED.net_income_ttm, filing_facts.net_income_ttm),
            eps_ttm = COALESCE(EXCLUDED.eps_ttm, filing_facts.eps_ttm),
            raw_payload = EXCLUDED.raw_payload,
            source = EXCLUDED.source
        """
    )

    inserted = 0
    with engine.begin() as conn:
        symbols = conn.execute(symbols_sql, {'max_symbols': max_symbols}).mappings().all()
        for symbol in symbols:
            cik = symbol['cik']
            url = f"{settings.sec_base_url}/api/xbrl/companyfacts/CIK{cik}.json"
            try:
                payload = _fetch_json(client, url)
                us_gaap = payload.get('facts', {}).get('us-gaap', {})
                revenues = us_gaap.get('Revenues', {}).get('units', {}).get('USD', [])
                income = us_gaap.get('NetIncomeLoss', {}).get('units', {}).get('USD', [])
                eps = us_gaap.get('EarningsPerShareDiluted', {}).get('units', {}).get('USD/shares', [])

                rev_latest = revenues[-1] if revenues else None
                ni_latest = income[-1] if income else None
                eps_latest = eps[-1] if eps else None

                filing = rev_latest or ni_latest or eps_latest
                if not filing:
                    continue

                filing_date = datetime.strptime(filing.get('filed'), '%Y-%m-%d').date()
                period_end = datetime.strptime(filing.get('end'), '%Y-%m-%d').date()

                conn.execute(
                    upsert_sql,
                    {
                        'symbol_id': symbol['id'],
                        'filing_date': filing_date,
                        'period_end_date': period_end,
                        'revenue_ttm': rev_latest.get('val') if rev_latest else None,
                        'net_income_ttm': ni_latest.get('val') if ni_latest else None,
                        'eps_ttm': eps_latest.get('val') if eps_latest else None,
                        'raw_payload': str({'fetched_at': datetime.now(UTC).isoformat(), 'ticker': symbol['ticker'], 'cik': cik}).replace("'", '"'),
                    },
                )
                inserted += 1
            except Exception as exc:  # noqa: BLE001
                logger.exception('Failed filing sync ticker=%s cik=%s: %s', symbol['ticker'], cik, exc)

    logger.info('SEC filing sync complete: %s upserts', inserted)
    return inserted
