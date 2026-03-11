from __future__ import annotations

from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .models import FactorScoreDaily, FilingFact, PriceDaily, Recommendation, Symbol
from .schemas import (
    HealthResponse,
    PaginationMeta,
    PriceHistoryItem,
    PriceHistoryResponse,
    RankingItem,
    RankingsResponse,
    RecommendationItem,
    RecommendationsLatestResponse,
    StockDetailResponse,
    TopPicksResponse,
    TurnaroundItem,
    TurnaroundResponse,
)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


def _pagination(page: int, size: int) -> tuple[int, int]:
    return (page - 1) * size, size


@app.get('/health', tags=['health'], response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(status='ok')


@app.get('/top-picks', tags=['rankings'], response_model=TopPicksResponse)
def top_picks(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
) -> TopPicksResponse:
    offset, limit = _pagination(page, size)

    latest_date = db.scalar(select(func.max(Recommendation.recommendation_date)))
    if latest_date is None:
        return TopPicksResponse(items=[], meta=PaginationMeta(page=page, size=size, total=0))

    base_query = (
        select(Recommendation, Symbol.ticker, Symbol.name)
        .join(Symbol, Symbol.id == Recommendation.symbol_id)
        .where(Recommendation.recommendation_date == latest_date)
    )

    if q:
        query = f"%{q.strip().upper()}%"
        base_query = base_query.where(func.upper(Symbol.ticker).like(query) | func.upper(func.coalesce(Symbol.name, '')).like(query))

    base_query = base_query.order_by(Recommendation.conviction.desc().nullslast(), Symbol.ticker.asc())

    total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
    rows = db.execute(base_query.offset(offset).limit(limit)).all()

    items = [
        RecommendationItem(
            symbol=ticker,
            name=name,
            recommendation_date=rec.recommendation_date,
            action=rec.action.value,
            conviction=float(rec.conviction) if rec.conviction is not None else None,
            target_price=float(rec.target_price) if rec.target_price is not None else None,
            horizon_days=rec.horizon_days,
            rationale=rec.rationale,
        )
        for rec, ticker, name in rows
    ]

    return TopPicksResponse(items=items, meta=PaginationMeta(page=page, size=size, total=total))


@app.get('/rankings', tags=['rankings'], response_model=RankingsResponse)
def rankings(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
) -> RankingsResponse:
    offset, limit = _pagination(page, size)

    latest_date = db.scalar(select(func.max(FactorScoreDaily.score_date)))
    if latest_date is None:
        return RankingsResponse(items=[], meta=PaginationMeta(page=page, size=size, total=0))

    ranked_query = (
        select(
            Symbol.ticker.label('symbol'),
            Symbol.name.label('name'),
            FactorScoreDaily.score_date.label('score_date'),
            func.avg(FactorScoreDaily.score).label('final_score'),
        )
        .join(Symbol, Symbol.id == FactorScoreDaily.symbol_id)
        .where(FactorScoreDaily.score_date == latest_date)
    )

    if q:
        query = f"%{q.strip().upper()}%"
        ranked_query = ranked_query.where(func.upper(Symbol.ticker).like(query) | func.upper(func.coalesce(Symbol.name, '')).like(query))

    ranked_subquery = ranked_query.group_by(Symbol.ticker, Symbol.name, FactorScoreDaily.score_date).subquery()

    total = db.scalar(select(func.count()).select_from(ranked_subquery)) or 0
    rows = db.execute(
        select(ranked_subquery)
        .order_by(ranked_subquery.c.final_score.desc(), ranked_subquery.c.symbol.asc())
        .offset(offset)
        .limit(limit)
    ).all()

    items = [
        RankingItem(
            symbol=row.symbol,
            name=row.name,
            score_date=row.score_date,
            final_score=float(row.final_score) if row.final_score is not None else 0.0,
        )
        for row in rows
    ]

    return RankingsResponse(items=items, meta=PaginationMeta(page=page, size=size, total=total))


@app.get('/stocks/{symbol}', tags=['stocks'], response_model=StockDetailResponse)
def stock_detail(symbol: str, db: Session = Depends(get_db)) -> StockDetailResponse:
    ticker = symbol.upper()
    stock = db.scalar(select(Symbol).where(Symbol.ticker == ticker))
    if stock is None:
        raise HTTPException(status_code=404, detail=f'Symbol not found: {ticker}')

    latest_price = db.execute(
        select(PriceDaily)
        .where(PriceDaily.symbol_id == stock.id)
        .order_by(PriceDaily.price_date.desc())
        .limit(1)
    ).scalar_one_or_none()

    latest_rec = db.execute(
        select(Recommendation)
        .where(Recommendation.symbol_id == stock.id)
        .order_by(Recommendation.recommendation_date.desc(), Recommendation.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    recommendation = None
    if latest_rec is not None:
        recommendation = RecommendationItem(
            symbol=ticker,
            recommendation_date=latest_rec.recommendation_date,
            action=latest_rec.action.value,
            conviction=float(latest_rec.conviction) if latest_rec.conviction is not None else None,
            target_price=float(latest_rec.target_price) if latest_rec.target_price is not None else None,
            horizon_days=latest_rec.horizon_days,
            rationale=latest_rec.rationale,
        )

    return StockDetailResponse(
        symbol=ticker,
        name=stock.name,
        exchange=stock.exchange,
        sector=stock.sector,
        industry=stock.industry,
        cik=stock.cik,
        sic=stock.sic,
        latest_close=float(latest_price.close) if latest_price and latest_price.close is not None else None,
        latest_price_date=latest_price.price_date if latest_price else None,
        latest_recommendation=recommendation,
    )


@app.get('/stocks/{symbol}/history', tags=['stocks'], response_model=PriceHistoryResponse)
def stock_history(
    symbol: str,
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> PriceHistoryResponse:
    ticker = symbol.upper()
    stock = db.scalar(select(Symbol).where(Symbol.ticker == ticker))
    if stock is None:
        raise HTTPException(status_code=404, detail=f'Symbol not found: {ticker}')

    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail='start_date must be <= end_date')

    offset, limit = _pagination(page, size)
    filters = [PriceDaily.symbol_id == stock.id]
    if start_date:
        filters.append(PriceDaily.price_date >= start_date)
    if end_date:
        filters.append(PriceDaily.price_date <= end_date)

    base_query = select(PriceDaily).where(and_(*filters))
    total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
    rows = db.execute(
        base_query.order_by(PriceDaily.price_date.desc()).offset(offset).limit(limit)
    ).scalars().all()

    items = [
        PriceHistoryItem(
            price_date=row.price_date,
            open=float(row.open) if row.open is not None else None,
            high=float(row.high) if row.high is not None else None,
            low=float(row.low) if row.low is not None else None,
            close=float(row.close) if row.close is not None else None,
            adjusted_close=float(row.adjusted_close) if row.adjusted_close is not None else None,
            volume=row.volume,
        )
        for row in rows
    ]

    return PriceHistoryResponse(
        symbol=ticker,
        items=items,
        meta=PaginationMeta(page=page, size=size, total=total),
    )


@app.get('/recommendations/latest', tags=['rankings'], response_model=RecommendationsLatestResponse)
def recommendations_latest(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> RecommendationsLatestResponse:
    latest_date = db.scalar(select(func.max(Recommendation.recommendation_date)))
    if latest_date is None:
        return RecommendationsLatestResponse(as_of_date=None, items=[])

    rows = db.execute(
        select(Recommendation, Symbol.ticker, Symbol.name)
        .join(Symbol, Symbol.id == Recommendation.symbol_id)
        .where(Recommendation.recommendation_date == latest_date)
        .order_by(Recommendation.conviction.desc().nullslast(), Symbol.ticker.asc())
        .limit(limit)
    ).all()

    items = [
        RecommendationItem(
            symbol=ticker,
            name=name,
            recommendation_date=rec.recommendation_date,
            action=rec.action.value,
            conviction=float(rec.conviction) if rec.conviction is not None else None,
            target_price=float(rec.target_price) if rec.target_price is not None else None,
            horizon_days=rec.horizon_days,
            rationale=rec.rationale,
        )
        for rec, ticker, name in rows
    ]
    return RecommendationsLatestResponse(as_of_date=latest_date, items=items)


@app.get('/turnarounds', tags=['rankings'], response_model=TurnaroundResponse)
def turnarounds(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> TurnaroundResponse:
    offset, limit = _pagination(page, size)

    year_col = func.extract('year', FilingFact.period_end_date).cast(int)
    yearly = (
        select(
            FilingFact.symbol_id.label('symbol_id'),
            year_col.label('year'),
            func.sum(func.coalesce(FilingFact.net_income_ttm, 0)).label('net_income'),
        )
        .group_by(FilingFact.symbol_id, year_col)
        .subquery()
    )

    y0 = yearly.alias('y0')
    y2 = yearly.alias('y2')

    candidates = (
        select(
            y0.c.symbol_id.label('symbol_id'),
            y0.c.year.label('base_year'),
            y0.c.net_income.label('base_year_net_income'),
            y2.c.year.label('turnaround_year'),
            y2.c.net_income.label('turnaround_year_net_income'),
        )
        .join(
            y2,
            and_(
                y2.c.symbol_id == y0.c.symbol_id,
                y2.c.year == y0.c.year + 2,
            ),
        )
        .where(
            y0.c.net_income < 0,
            y2.c.net_income > 0,
        )
        .subquery()
    )

    base_query = (
        select(
            Symbol.ticker.label('symbol'),
            Symbol.name.label('name'),
            candidates.c.base_year,
            (candidates.c.base_year + 1).label('next_year'),
            candidates.c.turnaround_year,
            candidates.c.base_year_net_income,
            candidates.c.turnaround_year_net_income,
        )
        .join(Symbol, Symbol.id == candidates.c.symbol_id)
        .where(Symbol.is_active == True)  # noqa: E712
        .order_by(
            candidates.c.turnaround_year.desc(),
            candidates.c.turnaround_year_net_income.desc(),
            Symbol.ticker.asc(),
        )
    )

    total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
    rows = db.execute(base_query.offset(offset).limit(limit)).all()

    items = [
        TurnaroundItem(
            symbol=row.symbol,
            name=row.name,
            base_year=int(row.base_year),
            next_year=int(row.next_year),
            turnaround_year=int(row.turnaround_year),
            base_year_net_income=float(row.base_year_net_income),
            turnaround_year_net_income=float(row.turnaround_year_net_income),
        )
        for row in rows
    ]

    return TurnaroundResponse(items=items, meta=PaginationMeta(page=page, size=size, total=total))

