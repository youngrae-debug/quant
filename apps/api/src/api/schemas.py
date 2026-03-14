from __future__ import annotations

from datetime import date, datetime

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




class BuffettChecklistData(BaseModel):
    latest_filing_date: date | None
    financial_years_available: int
    revenue_ttm: float | None
    ebit_ttm: float | None
    free_cash_flow_ttm: float | None
    roic_ttm: float | None
    total_debt: float | None
    net_debt: float | None
    interest_expense_ttm: float | None
    interest_coverage: float | None
    debt_maturity_profile: str | None
    dividends_ttm: float | None
    buybacks_ttm: float | None
    capex_ttm: float | None

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
    buffett_checklist: BuffettChecklistData


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


class StockCommentItem(BaseModel):
    id: int
    symbol: str
    nickname: str
    content: str
    created_at: datetime


class StockCommentsResponse(BaseModel):
    items: list[StockCommentItem]
    meta: PaginationMeta


class StockCommentCreateRequest(BaseModel):
    nickname: str = Field(min_length=2, max_length=40)
    content: str = Field(min_length=1, max_length=2000)
