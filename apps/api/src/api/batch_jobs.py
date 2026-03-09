from __future__ import annotations

from datetime import date

from sqlalchemy import text

from .db import engine


def run_quant_scoring(as_of_date: date) -> int:
    """Idempotent scoring job: upsert factor_scores_daily for all symbols."""
    from quant_engine import calculate_factor_scores

    select_sql = text(
        """
        SELECT s.id AS symbol_id,
               f.pe_ratio,
               f.pb_ratio,
               f.revenue_ttm,
               f.eps_ttm,
               p.close,
               p.open
        FROM symbols s
        LEFT JOIN fundamentals_snapshot_daily f
          ON f.symbol_id = s.id AND f.as_of_date = :as_of_date
        LEFT JOIN price_daily p
          ON p.symbol_id = s.id AND p.price_date = :as_of_date
        WHERE s.is_active = true
        """
    )
    upsert_sql = text(
        """
        INSERT INTO factor_scores_daily (symbol_id, score_date, factor_name, score, model_version, created_at)
        VALUES (:symbol_id, :score_date, :factor_name, :score, 'v1', now())
        ON CONFLICT (symbol_id, score_date, factor_name)
        DO UPDATE SET
            score = EXCLUDED.score,
            model_version = EXCLUDED.model_version
        """
    )

    upserts = 0
    with engine.begin() as conn:
        rows = conn.execute(select_sql, {'as_of_date': as_of_date}).mappings().all()
        for row in rows:
            metrics = {
                'pe_ratio': float(row['pe_ratio']) if row['pe_ratio'] is not None else 30,
                'pb_ratio': float(row['pb_ratio']) if row['pb_ratio'] is not None else 5,
                'revenue_growth_yoy': 0,
                'eps_growth_yoy': 0,
                'gross_margin': 0.4,
                'roe': 0.12,
                'roa': 0.06,
                'return_3m': 0.0,
                'return_6m': 0.0,
                'eps_revision_3m': 0.0,
                'analyst_target_spread': 0.0,
            }
            factors = calculate_factor_scores(metrics)
            for factor_name, score in factors.items():
                conn.execute(
                    upsert_sql,
                    {
                        'symbol_id': row['symbol_id'],
                        'score_date': as_of_date,
                        'factor_name': factor_name,
                        'score': score,
                    },
                )
                upserts += 1

    return upserts


def refresh_recommendations(as_of_date: date) -> int:
    """Idempotent recommendation refresh from aggregated factor scores."""
    from quant_engine import map_rating

    select_sql = text(
        """
        SELECT fs.symbol_id, AVG(fs.score) AS final_score
        FROM factor_scores_daily fs
        WHERE fs.score_date = :as_of_date
        GROUP BY fs.symbol_id
        """
    )
    upsert_sql = text(
        """
        INSERT INTO recommendations (symbol_id, recommendation_date, action, conviction, rationale, created_at)
        VALUES (:symbol_id, :recommendation_date, :action::recommendation_action, :conviction, :rationale, now())
        ON CONFLICT (symbol_id, recommendation_date) DO UPDATE SET
            action = EXCLUDED.action,
            conviction = EXCLUDED.conviction,
            rationale = EXCLUDED.rationale
        """
    )

    inserted = 0
    with engine.begin() as conn:
        rows = conn.execute(select_sql, {'as_of_date': as_of_date}).mappings().all()
        for row in rows:
            score = float(row['final_score']) if row['final_score'] is not None else 50.0
            rating = map_rating(score)
            action_map = {
                'Strong Buy': 'buy',
                'Buy': 'buy',
                'Hold': 'hold',
                'Sell': 'sell',
                'Strong Sell': 'sell',
            }
            conn.execute(
                upsert_sql,
                {
                    'symbol_id': row['symbol_id'],
                    'recommendation_date': as_of_date,
                    'action': action_map[rating],
                    'conviction': min(1.0, max(0.0, score / 100.0)),
                    'rationale': f'Auto-refresh from quant engine score {score:.2f}',
                },
            )
            inserted += 1

    return inserted
