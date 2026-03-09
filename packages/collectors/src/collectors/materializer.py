from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import text

from .db import engine
from .logging import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class FilingFactRow:
    symbol_id: int
    filing_date: date
    period_end_date: date
    market_cap: Decimal | None
    pe_ratio: Decimal | None
    pb_ratio: Decimal | None
    eps_ttm: Decimal | None
    revenue_ttm: Decimal | None
    net_income_ttm: Decimal | None
    ebitda_ttm: Decimal | None


def materialize_daily_fundamentals(as_of_date: date) -> int:
    """
    Materialize PIT daily fundamentals without look-ahead bias.

    Rule: only facts whose filing_date <= as_of_date are eligible.
    For each symbol, choose the latest eligible filing.
    """

    # Placeholder source table expected from SEC filings/companyfacts ingestion stage.
    # This stage intentionally focuses on the PIT transformation contract.
    source_sql = text(
        """
        SELECT DISTINCT ON (ff.symbol_id)
            ff.symbol_id,
            ff.filing_date,
            ff.period_end_date,
            ff.market_cap,
            ff.pe_ratio,
            ff.pb_ratio,
            ff.eps_ttm,
            ff.revenue_ttm,
            ff.net_income_ttm,
            ff.ebitda_ttm
        FROM filing_facts ff
        WHERE ff.filing_date <= :as_of_date
        ORDER BY ff.symbol_id, ff.filing_date DESC, ff.period_end_date DESC
        """
    )

    upsert_sql = text(
        """
        INSERT INTO fundamentals_snapshot_daily
            (symbol_id, as_of_date, market_cap, pe_ratio, pb_ratio, eps_ttm, revenue_ttm, net_income_ttm, ebitda_ttm, source, created_at)
        VALUES
            (:symbol_id, :as_of_date, :market_cap, :pe_ratio, :pb_ratio, :eps_ttm, :revenue_ttm, :net_income_ttm, :ebitda_ttm, 'materializer', now())
        ON CONFLICT (symbol_id, as_of_date)
        DO UPDATE SET
            market_cap = EXCLUDED.market_cap,
            pe_ratio = EXCLUDED.pe_ratio,
            pb_ratio = EXCLUDED.pb_ratio,
            eps_ttm = EXCLUDED.eps_ttm,
            revenue_ttm = EXCLUDED.revenue_ttm,
            net_income_ttm = EXCLUDED.net_income_ttm,
            ebitda_ttm = EXCLUDED.ebitda_ttm,
            source = EXCLUDED.source
        """
    )

    upserted = 0
    with engine.begin() as conn:
        rows = conn.execute(source_sql, {'as_of_date': as_of_date}).mappings().all()
        for row in rows:
            conn.execute(
                upsert_sql,
                {
                    'symbol_id': row['symbol_id'],
                    'as_of_date': as_of_date,
                    'market_cap': row['market_cap'],
                    'pe_ratio': row['pe_ratio'],
                    'pb_ratio': row['pb_ratio'],
                    'eps_ttm': row['eps_ttm'],
                    'revenue_ttm': row['revenue_ttm'],
                    'net_income_ttm': row['net_income_ttm'],
                    'ebitda_ttm': row['ebitda_ttm'],
                },
            )
            upserted += 1

    logger.info('Fundamentals materializer complete for %s: %s rows', as_of_date, upserted)
    return upserted
