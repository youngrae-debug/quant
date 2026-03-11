from __future__ import annotations

import csv
import json
import re
import time
from datetime import UTC, date, datetime, timedelta
from io import StringIO
from typing import Any

import httpx
import yfinance as yf
from sqlalchemy import text

from .config import settings
from .db import engine
from .logging import get_logger

logger = get_logger(__name__)

_SUPPORTED_TICKER_PATTERN = re.compile(r'^[A-Z]{1,5}$')


class FinnhubForbiddenError(RuntimeError):
    """Raised when Finnhub denies access for the request (HTTP 403)."""


def _finnhub_request(client: httpx.Client, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    merged = dict(params)
    merged['token'] = settings.finnhub_api_key

    for attempt in range(1, 6):
        response = client.get(f'{settings.finnhub_base_url}/{endpoint}', params=merged)
        if response.status_code == 403:
            raise FinnhubForbiddenError(f'Finnhub request forbidden for {endpoint}')
        if response.status_code == 429:
            sleep_for = settings.rate_limit_sleep_seconds * attempt
            logger.warning('Finnhub rate limited; sleeping %.2fs', sleep_for)
            time.sleep(sleep_for)
            continue
        response.raise_for_status()
        return response.json()

    raise RuntimeError(f'Finnhub request failed after retries: {endpoint}')


def _parse_iso_date(value: str) -> date:
    return datetime.strptime(value, '%Y-%m-%d').date()  # noqa: DTZ007


def _fetch_yfinance_daily_prices(
    _: httpx.Client,
    *,
    ticker: str,
    start_date: date,
    until_date: date,
) -> list[dict[str, Any]]:
    history = yf.download(
        ticker,
        start=start_date.isoformat(),
        end=(until_date + timedelta(days=1)).isoformat(),
        interval='1d',
        auto_adjust=False,
        progress=False,
    )
    if history.empty:
        return []

    rows: list[dict[str, Any]] = []
    for idx, row in history.iterrows():
        price_date = idx.date()
        adj_close = row['Adj Close'] if 'Adj Close' in row else row['Close']
        rows.append(
            {
                'price_date': price_date,
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'adjusted_close': float(adj_close),
                'volume': int(row['Volume']),
                'source': 'yfinance',
            }
        )
    return rows


def _fetch_finnhub_daily_prices(
    client: httpx.Client,
    *,
    ticker: str,
    start_date: date,
    until_date: date,
) -> list[dict[str, Any]]:
    if not settings.finnhub_api_key:
        return []

    payload = _finnhub_request(
        client,
        'stock/candle',
        {
            'symbol': ticker,
            'resolution': 'D',
            'from': int(datetime.combine(start_date, datetime.min.time(), tzinfo=UTC).timestamp()),
            'to': int(datetime.combine(until_date, datetime.min.time(), tzinfo=UTC).timestamp()),
        },
    )
    if payload.get('s') != 'ok':
        logger.warning('No Finnhub candle data for %s: %s', ticker, payload.get('s'))
        return []

    return [
        {
            'price_date': datetime.fromtimestamp(ts, tz=UTC).date(),
            'open': payload['o'][idx],
            'high': payload['h'][idx],
            'low': payload['l'][idx],
            'close': payload['c'][idx],
            'adjusted_close': payload['c'][idx],
            'volume': payload['v'][idx],
            'source': 'finnhub',
        }
        for idx, ts in enumerate(payload.get('t', []))
    ]


def _fetch_alpha_vantage_daily_prices(
    client: httpx.Client,
    *,
    ticker: str,
    start_date: date,
    until_date: date,
) -> list[dict[str, Any]]:
    if not settings.alpha_vantage_api_key:
        return []

    response = client.get(
        'https://www.alphavantage.co/query',
        params={
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': ticker,
            'outputsize': 'full',
            'apikey': settings.alpha_vantage_api_key,
        },
    )
    response.raise_for_status()
    payload = response.json()

    series = payload.get('Time Series (Daily)')
    if not isinstance(series, dict):
        if 'Note' in payload:
            logger.warning('Alpha Vantage rate limited for %s: %s', ticker, payload['Note'])
        elif 'Error Message' in payload:
            logger.warning('Alpha Vantage returned error for %s: %s', ticker, payload['Error Message'])
        return []

    rows: list[dict[str, Any]] = []
    for day, values in series.items():
        price_date = _parse_iso_date(day)
        if price_date < start_date or price_date > until_date:
            continue
        rows.append(
            {
                'price_date': price_date,
                'open': float(values['1. open']),
                'high': float(values['2. high']),
                'low': float(values['3. low']),
                'close': float(values['4. close']),
                'adjusted_close': float(values['5. adjusted close']),
                'volume': int(values['6. volume']),
                'source': 'alpha_vantage',
            }
        )

    rows.sort(key=lambda item: item['price_date'])
    return rows


def _fetch_twelvedata_daily_prices(
    client: httpx.Client,
    *,
    ticker: str,
    start_date: date,
    until_date: date,
) -> list[dict[str, Any]]:
    if not settings.twelvedata_api_key:
        return []

    response = client.get(
        'https://api.twelvedata.com/time_series',
        params={
            'symbol': ticker,
            'interval': '1day',
            'start_date': start_date.isoformat(),
            'end_date': until_date.isoformat(),
            'apikey': settings.twelvedata_api_key,
            'outputsize': 5000,
            'format': 'JSON',
        },
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get('status') == 'error':
        logger.warning('Twelve Data returned error for %s: %s', ticker, payload.get('message'))
        return []

    values = payload.get('values')
    if not isinstance(values, list):
        return []

    rows = [
        {
            'price_date': _parse_iso_date(str(item['datetime'])[:10]),
            'open': float(item['open']),
            'high': float(item['high']),
            'low': float(item['low']),
            'close': float(item['close']),
            'adjusted_close': float(item['close']),
            'volume': int(float(item.get('volume', 0) or 0)),
            'source': 'twelvedata',
        }
        for item in values
    ]
    rows.sort(key=lambda item: item['price_date'])
    return rows


def _fetch_stooq_daily_prices(
    client: httpx.Client,
    *,
    ticker: str,
    start_date: date,
    until_date: date,
) -> list[dict[str, Any]]:
    response = client.get('https://stooq.com/q/d/l/', params={'s': f'{ticker.lower()}.us', 'i': 'd'})
    response.raise_for_status()

    reader = csv.DictReader(StringIO(response.text))
    rows: list[dict[str, Any]] = []
    for row in reader:
        if not row.get('Date'):
            continue
        price_date = _parse_iso_date(row['Date'])
        if price_date < start_date or price_date > until_date:
            continue
        rows.append(
            {
                'price_date': price_date,
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'adjusted_close': float(row['Close']),
                'volume': int(float(row['Volume'])),
                'source': 'stooq',
            }
        )

    return rows


def _fallback_prices(
    client: httpx.Client,
    *,
    ticker: str,
    start_date: date,
    until_date: date,
) -> list[dict[str, Any]]:
    provider_fetchers: dict[str, Any] = {
        'finnhub': _fetch_finnhub_daily_prices,
        'twelvedata': _fetch_twelvedata_daily_prices,
        'alphavantage': _fetch_alpha_vantage_daily_prices,
        'stooq': _fetch_stooq_daily_prices,
    }
    fallback_chain = tuple(
        provider.strip().lower()
        for provider in settings.price_fallback_providers.split(',')
        if provider.strip()
    )

    for provider in fallback_chain:
        fetcher = provider_fetchers.get(provider)
        if fetcher is None:
            logger.warning('Unknown fallback provider configured: %s', provider)
            continue
        try:
            rows = fetcher(client, ticker=ticker, start_date=start_date, until_date=until_date)
            if rows:
                logger.info('Fallback provider %s used for %s (%s rows)', provider, ticker, len(rows))
                return rows
        except FinnhubForbiddenError:
            logger.warning('Finnhub forbidden for %s; continuing fallback chain', ticker)
        except Exception as exc:  # noqa: BLE001
            logger.warning('Fallback provider %s failed for %s: %s', provider, ticker, exc)

    return []

def _fetch_symbol_prices(
    client: httpx.Client,
    *,
    ticker: str,
    start_date: date,
    until_date: date,
) -> list[dict[str, Any]]:
    try:
        rows = _fetch_yfinance_daily_prices(client, ticker=ticker, start_date=start_date, until_date=until_date)
        if rows:
            return rows
    except Exception as exc:  # noqa: BLE001
        logger.warning('Primary provider yfinance failed for %s: %s', ticker, exc)

    return _fallback_prices(client, ticker=ticker, start_date=start_date, until_date=until_date)


def _resolve_sync_start(last_price_date: date | None) -> date:
    if last_price_date is None:
        return datetime.now(UTC).date() - timedelta(days=settings.symbol_default_lookback_days)
    return last_price_date + timedelta(days=1)


def _is_supported_ticker(ticker: str) -> bool:
    return bool(_SUPPORTED_TICKER_PATTERN.fullmatch(ticker))


def sync_daily_prices(
    until: date | None = None,
    max_symbols: int | None = None,
    allowed_exchanges: tuple[str, ...] = ('Nasdaq', 'NYSE'),
) -> int:
    until_date = until or datetime.now(UTC).date()
    updated_rows = 0
    inserted_rows = 0
    source_totals: dict[str, int] = {}

    symbols_sql = text(
        """
        SELECT s.id, s.ticker, s.exchange, MAX(p.price_date) AS last_price_date
        FROM symbols s
        LEFT JOIN price_daily p ON p.symbol_id = s.id
        WHERE s.is_active = true
        GROUP BY s.id, s.ticker, s.exchange
        ORDER BY s.id
        """
    )

    upsert_sql = text(
        """
        INSERT INTO price_daily
            (symbol_id, price_date, open, high, low, close, adjusted_close, volume, source, created_at)
        VALUES
            (:symbol_id, :price_date, :open, :high, :low, :close, :adjusted_close, :volume, :source, now())
        ON CONFLICT (symbol_id, price_date)
        DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            adjusted_close = EXCLUDED.adjusted_close,
            volume = EXCLUDED.volume,
            source = EXCLUDED.source
        RETURNING (xmax = 0) AS inserted
        """
    )

    with engine.begin() as conn:
        symbols = conn.execute(symbols_sql).mappings().all()

    filtered_symbols = [
        symbol
        for symbol in symbols
        if _is_supported_ticker(str(symbol['ticker'])) and (symbol['exchange'] in allowed_exchanges)
    ]

    if max_symbols is not None and max_symbols > 0:
        filtered_symbols = filtered_symbols[:max_symbols]

    logger.info('Price sync candidates: %s (filtered from %s)', len(filtered_symbols), len(symbols))

    with httpx.Client(timeout=settings.request_timeout_seconds) as client:
        with engine.begin() as conn:
            for symbol in filtered_symbols:
                ticker = symbol['ticker']
                start_date = _resolve_sync_start(symbol['last_price_date'])
                if start_date > until_date:
                    continue

                try:
                    price_rows = _fetch_symbol_prices(
                        client,
                        ticker=ticker,
                        start_date=start_date,
                        until_date=until_date,
                    )
                    if not price_rows:
                        continue

                    for row in price_rows:
                        was_inserted = conn.execute(
                            upsert_sql,
                            {
                                'symbol_id': symbol['id'],
                                **row,
                            },
                        ).scalar_one()

                        updated_rows += 1
                        inserted_rows += int(bool(was_inserted))
                        source = str(row['source'])
                        source_totals[source] = source_totals.get(source, 0) + 1
                except Exception as exc:  # noqa: BLE001
                    logger.exception('Failed price sync for %s: %s', ticker, exc)

    logger.info(
        'Price sync complete: %s rows upserted (%s inserted, %s updated)',
        updated_rows,
        inserted_rows,
        updated_rows - inserted_rows,
    )
    if source_totals:
        logger.info('Price sync source breakdown (upserts): %s', source_totals)
    return updated_rows



def sync_yfinance_symbol_info(max_symbols: int = 500) -> int:
        """Enrich symbols with sector/industry and fundamentals data from yfinance."""
        symbols_sql = text(
            """
            SELECT id, ticker
            FROM symbols
            WHERE is_active = true
              AND exchange IN ('Nasdaq', 'NYSE')
              AND ticker ~ '^[A-Z]{1,5}$'
            ORDER BY id
            LIMIT :max_symbols
            """
        )
        update_symbol_sql = text(
            """
            UPDATE symbols
            SET sector = :sector, industry = :industry, updated_at = now()
            WHERE id = :id
            """
        )
        upsert_filing_sql = text(
            """
            INSERT INTO filing_facts (
                symbol_id, filing_date, period_end_date,
                market_cap, pe_ratio, pb_ratio, eps_ttm, revenue_ttm, net_income_ttm,
                source, raw_payload, created_at
            ) VALUES (
                :symbol_id, :filing_date, :period_end_date,
                :market_cap, :pe_ratio, :pb_ratio, :eps_ttm, :revenue_ttm, :net_income_ttm,
                'yfinance', CAST(:raw_payload AS jsonb), now()
            )
            ON CONFLICT (symbol_id, filing_date, period_end_date)
            DO UPDATE SET
                market_cap = COALESCE(EXCLUDED.market_cap, filing_facts.market_cap),
                pe_ratio = COALESCE(EXCLUDED.pe_ratio, filing_facts.pe_ratio),
                pb_ratio = COALESCE(EXCLUDED.pb_ratio, filing_facts.pb_ratio),
                eps_ttm = COALESCE(EXCLUDED.eps_ttm, filing_facts.eps_ttm),
                revenue_ttm = COALESCE(EXCLUDED.revenue_ttm, filing_facts.revenue_ttm),
                net_income_ttm = COALESCE(EXCLUDED.net_income_ttm, filing_facts.net_income_ttm),
                source = EXCLUDED.source,
                raw_payload = EXCLUDED.raw_payload
            """
        )

        today = datetime.now(UTC).date()
        enriched = 0

        with engine.connect() as read_conn:
            symbols = read_conn.execute(symbols_sql, {'max_symbols': max_symbols}).mappings().all()

        for symbol in symbols:
            ticker = str(symbol['ticker'])
            try:
                info = yf.Ticker(ticker).info
                if not info or not isinstance(info, dict):
                    continue

                sector = info.get('sector') or None
                industry = info.get('industry') or None
                pe_ratio = info.get('trailingPE') or info.get('forwardPE') or None
                pb_ratio = info.get('priceToBook') or None
                market_cap = info.get('marketCap') or None
                eps_ttm = info.get('trailingEps') or None
                revenue_ttm = info.get('totalRevenue') or None
                net_income_ttm = info.get('netIncomeToCommon') or None

                has_meta = bool(sector or industry)
                has_fundamentals = any(
                    v is not None for v in [pe_ratio, pb_ratio, market_cap, eps_ttm, revenue_ttm]
                )

                if not has_meta and not has_fundamentals:
                    continue

                with engine.begin() as conn:
                    if has_meta:
                        conn.execute(
                            update_symbol_sql,
                            {'id': symbol['id'], 'sector': sector, 'industry': industry},
                        )

                    if has_fundamentals:
                        raw = json.dumps({
                            'ticker': ticker,
                            'fetched_at': datetime.now(UTC).isoformat(),
                            'sector': sector,
                            'industry': industry,
                        })
                        conn.execute(
                            upsert_filing_sql,
                            {
                                'symbol_id': symbol['id'],
                                'filing_date': today,
                                'period_end_date': today,
                                'market_cap': market_cap,
                                'pe_ratio': pe_ratio,
                                'pb_ratio': pb_ratio,
                                'eps_ttm': eps_ttm,
                                'revenue_ttm': revenue_ttm,
                                'net_income_ttm': net_income_ttm,
                                'raw_payload': raw,
                            },
                        )

                enriched += 1
                if enriched % 50 == 0:
                    logger.info('yfinance symbol info progress: %s enriched', enriched)

            except Exception as exc:  # noqa: BLE001
                logger.warning('yfinance info failed for %s: %s', ticker, exc)

            time.sleep(0.05)

        logger.info('yfinance symbol info enrichment complete: %s enriched out of %s', enriched, len(symbols))
        return enriched
