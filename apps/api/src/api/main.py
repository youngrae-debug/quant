from __future__ import annotations

from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .models import FactorScoreDaily, PriceDaily, Recommendation, Symbol
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
    db: Session = Depends(get_db),
) -> TopPicksResponse:
    offset, limit = _pagination(page, size)

    latest_date = db.scalar(select(func.max(Recommendation.recommendation_date)))
    if latest_date is None:
        return TopPicksResponse(items=[], meta=PaginationMeta(page=page, size=size, total=0))

    base_query = (
        select(Recommendation, Symbol.ticker)
        .join(Symbol, Symbol.id == Recommendation.symbol_id)
        .where(Recommendation.recommendation_date == latest_date)
        .order_by(Recommendation.conviction.desc().nullslast(), Symbol.ticker.asc())
    )

    total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
    rows = db.execute(base_query.offset(offset).limit(limit)).all()

    items = [
        RecommendationItem(
            symbol=ticker,
            recommendation_date=rec.recommendation_date,
            action=rec.action.value,
            conviction=float(rec.conviction) if rec.conviction is not None else None,
            target_price=float(rec.target_price) if rec.target_price is not None else None,
            horizon_days=rec.horizon_days,
            rationale=rec.rationale,
        )
        for rec, ticker in rows
    ]

    return TopPicksResponse(items=items, meta=PaginationMeta(page=page, size=size, total=total))


@app.get('/rankings', tags=['rankings'], response_model=RankingsResponse)
def rankings(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> RankingsResponse:
    offset, limit = _pagination(page, size)

    latest_date = db.scalar(select(func.max(FactorScoreDaily.score_date)))
    if latest_date is None:
        return RankingsResponse(items=[], meta=PaginationMeta(page=page, size=size, total=0))

    ranked_subquery = (
        select(
            Symbol.ticker.label('symbol'),
            FactorScoreDaily.score_date.label('score_date'),
            func.avg(FactorScoreDaily.score).label('final_score'),
        )
        .join(Symbol, Symbol.id == FactorScoreDaily.symbol_id)
        .where(FactorScoreDaily.score_date == latest_date)
        .group_by(Symbol.ticker, FactorScoreDaily.score_date)
        .subquery()
    )

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
        select(Recommendation, Symbol.ticker)
        .join(Symbol, Symbol.id == Recommendation.symbol_id)
        .where(Recommendation.recommendation_date == latest_date)
        .order_by(Recommendation.conviction.desc().nullslast(), Symbol.ticker.asc())
        .limit(limit)
    ).all()

    items = [
        RecommendationItem(
            symbol=ticker,
            recommendation_date=rec.recommendation_date,
            action=rec.action.value,
            conviction=float(rec.conviction) if rec.conviction is not None else None,
            target_price=float(rec.target_price) if rec.target_price is not None else None,
            horizon_days=rec.horizon_days,
            rationale=rec.rationale,
        )
        for rec, ticker in rows
    ]
    return RecommendationsLatestResponse(as_of_date=latest_date, items=items)
