from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class PaginationMeta(BaseModel):
    page: int
    size: int
    total: int


class PaginatedResponse(BaseModel):
    items: list
    meta: PaginationMeta


class RecommendationItem(BaseModel):
    symbol: str
    name: str | None = None
    recommendation_date: date
    action: str
    conviction: float | None
    target_price: float | None
    horizon_days: int | None
    rationale: str | None


class RankingItem(BaseModel):
    symbol: str
    name: str | None = None
    score_date: date
    final_score: float


class StockDetailResponse(BaseModel):
    symbol: str
    name: str | None
    exchange: str | None
    sector: str | None
    industry: str | None
    cik: str | None
    sic: str | None
    latest_close: float | None
    latest_price_date: date | None
    latest_recommendation: RecommendationItem | None


class PriceHistoryItem(BaseModel):
    price_date: date
    open: float | None
    high: float | None
    low: float | None
    close: float | None
    adjusted_close: float | None
    volume: int | None


class TopPicksResponse(BaseModel):
    items: list[RecommendationItem]
    meta: PaginationMeta


class RankingsResponse(BaseModel):
    items: list[RankingItem]
    meta: PaginationMeta


class PriceHistoryResponse(BaseModel):
    symbol: str
    items: list[PriceHistoryItem]
    meta: PaginationMeta


class RecommendationsLatestResponse(BaseModel):
    as_of_date: date | None = Field(default=None)
    items: list[RecommendationItem]


class TurnaroundItem(BaseModel):
    symbol: str
    name: str | None
    base_year: int
    next_year: int
    turnaround_year: int
    base_year_net_income: float
    turnaround_year_net_income: float


class TurnaroundResponse(BaseModel):
    items: list[TurnaroundItem]
    meta: PaginationMeta
