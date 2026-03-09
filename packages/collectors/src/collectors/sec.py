from __future__ import annotations

import time
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
