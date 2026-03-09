from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable


FACTOR_NAMES = ('value', 'growth', 'profitability', 'momentum', 'expectation')


@dataclass(slots=True)
class SymbolFactorSnapshot:
    symbol: str
    sector: str
    factor_scores: dict[str, float]


@dataclass(slots=True)
class RankingResult:
    symbol: str
    sector: str
    factor_percentiles: dict[str, float]
    final_score: float
    rating: str


def clamp_score(value: float) -> float:
    return max(0.0, min(100.0, float(value)))


def normalize_metric(value: float, min_value: float, max_value: float, inverse: bool = False) -> float:
    if max_value <= min_value:
        return 50.0
    raw = (value - min_value) / (max_value - min_value)
    if inverse:
        raw = 1 - raw
    return clamp_score(raw * 100)


def _mean(values: Iterable[float]) -> float:
    items = [float(v) for v in values]
    if not items:
        return 50.0
    return sum(items) / len(items)


def calculate_factor_scores(metrics: dict[str, float]) -> dict[str, float]:
    value = _mean(
        [
            normalize_metric(metrics.get('pe_ratio', 30), 5, 60, inverse=True),
            normalize_metric(metrics.get('pb_ratio', 6), 0.3, 15, inverse=True),
        ]
    )

    growth = _mean(
        [
            normalize_metric(metrics.get('revenue_growth_yoy', 0), -0.3, 0.8),
            normalize_metric(metrics.get('eps_growth_yoy', 0), -0.5, 1.0),
        ]
    )

    profitability = _mean(
        [
            normalize_metric(metrics.get('gross_margin', 0.35), 0.0, 0.8),
            normalize_metric(metrics.get('roe', 0.1), -0.2, 0.5),
            normalize_metric(metrics.get('roa', 0.05), -0.1, 0.3),
        ]
    )

    momentum = _mean(
        [
            normalize_metric(metrics.get('return_3m', 0), -0.4, 0.6),
            normalize_metric(metrics.get('return_6m', 0), -0.5, 1.0),
        ]
    )

    expectation = _mean(
        [
            normalize_metric(metrics.get('eps_revision_3m', 0), -0.3, 0.4),
            normalize_metric(metrics.get('analyst_target_spread', 0), -0.3, 0.5),
        ]
    )

    return {
        'value': round(value, 4),
        'growth': round(growth, 4),
        'profitability': round(profitability, 4),
        'momentum': round(momentum, 4),
        'expectation': round(expectation, 4),
    }


def _percentile_rank(value: float, peer_values: list[float]) -> float:
    if not peer_values:
        return 50.0
    less_or_equal = sum(1 for peer in peer_values if peer <= value)
    rank = less_or_equal / len(peer_values)
    return clamp_score(rank * 100)


def sector_relative_percentiles(
    snapshots: list[SymbolFactorSnapshot],
    weights: dict[str, float] | None = None,
) -> list[RankingResult]:
    weights = weights or {name: 1.0 for name in FACTOR_NAMES}

    by_sector: dict[str, list[SymbolFactorSnapshot]] = {}
    for snapshot in snapshots:
        by_sector.setdefault(snapshot.sector, []).append(snapshot)

    results: list[RankingResult] = []

    for sector, members in by_sector.items():
        peers_by_factor = {
            factor: [member.factor_scores.get(factor, 50.0) for member in members]
            for factor in FACTOR_NAMES
        }
        for member in members:
            percentiles = {
                factor: round(_percentile_rank(member.factor_scores.get(factor, 50.0), peers_by_factor[factor]), 4)
                for factor in FACTOR_NAMES
            }
            final_score = calculate_final_score(percentiles, weights=weights)
            results.append(
                RankingResult(
                    symbol=member.symbol,
                    sector=sector,
                    factor_percentiles=percentiles,
                    final_score=final_score,
                    rating=map_rating(final_score),
                )
            )

    return results


def calculate_final_score(factor_scores: dict[str, float], weights: dict[str, float] | None = None) -> float:
    weights = weights or {name: 1.0 for name in FACTOR_NAMES}
    weighted_sum = 0.0
    weight_total = 0.0
    for factor in FACTOR_NAMES:
        weight = max(0.0, float(weights.get(factor, 0.0)))
        weighted_sum += clamp_score(factor_scores.get(factor, 50.0)) * weight
        weight_total += weight

    if weight_total == 0:
        return 50.0
    return round(clamp_score(weighted_sum / weight_total), 4)


def map_rating(score: float) -> str:
    bounded = clamp_score(score)
    if bounded >= 85:
        return 'Strong Buy'
    if bounded >= 70:
        return 'Buy'
    if bounded >= 45:
        return 'Hold'
    if bounded >= 25:
        return 'Sell'
    return 'Strong Sell'


def strong_buy_streak(ratings_chronological: list[str]) -> int:
    streak = 0
    for rating in reversed(ratings_chronological):
        if rating == 'Strong Buy':
            streak += 1
        else:
            break
    return streak


def is_recommendation_in_cooldown(
    last_recommendation_date: date | None,
    as_of_date: date,
    cooldown_days: int,
) -> bool:
    if last_recommendation_date is None:
        return False
    if cooldown_days <= 0:
        return False
    days_since = (as_of_date - last_recommendation_date).days
    return days_since < cooldown_days
