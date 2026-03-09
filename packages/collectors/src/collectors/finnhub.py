from __future__ import annotations

import time
from datetime import UTC, date, datetime, timedelta
from typing import Any

import httpx
from sqlalchemy import text

from .config import settings
from .db import engine
from .logging import get_logger

logger = get_logger(__name__)


def _finnhub_request(client: httpx.Client, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    merged = dict(params)
    merged['token'] = settings.finnhub_api_key

    for attempt in range(1, 6):
        response = client.get(f'{settings.finnhub_base_url}/{endpoint}', params=merged)
        if response.status_code == 429:
            sleep_for = settings.rate_limit_sleep_seconds * attempt
            logger.warning('Finnhub rate limited; sleeping %.2fs', sleep_for)
            time.sleep(sleep_for)
            continue
        response.raise_for_status()
        return response.json()

    raise RuntimeError(f'Finnhub request failed after retries: {endpoint}')


def _resolve_sync_start(last_price_date: date | None) -> date:
    if last_price_date is None:
        return datetime.now(UTC).date() - timedelta(days=settings.symbol_default_lookback_days)
    return last_price_date + timedelta(days=1)


def sync_daily_prices(until: date | None = None) -> int:
    if not settings.finnhub_api_key:
        raise ValueError('FINNHUB_API_KEY is required for price sync')

    until_date = until or datetime.now(UTC).date()
    updated_rows = 0

    symbols_sql = text(
        """
        SELECT s.id, s.ticker, MAX(p.price_date) AS last_price_date
        FROM symbols s
        LEFT JOIN price_daily p ON p.symbol_id = s.id
        WHERE s.is_active = true
        GROUP BY s.id, s.ticker
        ORDER BY s.id
        """
    )

    upsert_sql = text(
        """
        INSERT INTO price_daily
            (symbol_id, price_date, open, high, low, close, adjusted_close, volume, source, created_at)
        VALUES
            (:symbol_id, :price_date, :open, :high, :low, :close, :adjusted_close, :volume, 'finnhub', now())
        ON CONFLICT (symbol_id, price_date)
        DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            adjusted_close = EXCLUDED.adjusted_close,
            volume = EXCLUDED.volume,
            source = EXCLUDED.source
        """
    )

    with engine.begin() as conn:
        symbols = conn.execute(symbols_sql).mappings().all()

    with httpx.Client(timeout=settings.request_timeout_seconds) as client:
        with engine.begin() as conn:
            for symbol in symbols:
                ticker = symbol['ticker']
                start_date = _resolve_sync_start(symbol['last_price_date'])
                if start_date > until_date:
                    continue

                try:
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
                        logger.warning('No candle data for %s: %s', ticker, payload.get('s'))
                        continue

                    for idx, ts in enumerate(payload.get('t', [])):
                        price_date = datetime.fromtimestamp(ts, tz=UTC).date()
                        conn.execute(
                            upsert_sql,
                            {
                                'symbol_id': symbol['id'],
                                'price_date': price_date,
                                'open': payload['o'][idx],
                                'high': payload['h'][idx],
                                'low': payload['l'][idx],
                                'close': payload['c'][idx],
                                'adjusted_close': payload['c'][idx],
                                'volume': payload['v'][idx],
                            },
                        )
                        updated_rows += 1
                except Exception as exc:  # noqa: BLE001
                    logger.exception('Failed price sync for %s: %s', ticker, exc)

    logger.info('Price sync complete: %s rows upserted', updated_rows)
    return updated_rows
