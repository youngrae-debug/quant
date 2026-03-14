from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Date, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class RecommendationAction(str, enum.Enum):
    buy = 'buy'
    hold = 'hold'
    sell = 'sell'


class Symbol(Base):
    __tablename__ = 'symbols'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), nullable=False, unique=True)
    cik: Mapped[str | None] = mapped_column(String(10))
    sic: Mapped[str | None] = mapped_column(String(8))
    name: Mapped[str | None] = mapped_column(String(255))
    exchange: Mapped[str | None] = mapped_column(String(64))
    sector: Mapped[str | None] = mapped_column(String(128))
    industry: Mapped[str | None] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(nullable=False, server_default='true')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    prices: Mapped[list['PriceDaily']] = relationship(back_populates='symbol')
    fundamentals: Mapped[list['FundamentalsSnapshotDaily']] = relationship(back_populates='symbol')
    factor_scores: Mapped[list['FactorScoreDaily']] = relationship(back_populates='symbol')
    recommendations: Mapped[list['Recommendation']] = relationship(back_populates='symbol')
    stock_comments: Mapped[list['StockComment']] = relationship(back_populates='symbol')
    filing_facts: Mapped[list['FilingFact']] = relationship(back_populates='symbol')


class PriceDaily(Base):
    __tablename__ = 'price_daily'
    __table_args__ = (
        UniqueConstraint('symbol_id', 'price_date', name='uq_price_daily_symbol_date'),
        Index('ix_price_daily_symbol_date', 'symbol_id', 'price_date'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    symbol_id: Mapped[int] = mapped_column(ForeignKey('symbols.id', ondelete='CASCADE'), nullable=False)
    price_date: Mapped[date] = mapped_column(Date, nullable=False)
    open: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    high: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    low: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    close: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    adjusted_close: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    volume: Mapped[int | None] = mapped_column(BigInteger)
    source: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    symbol: Mapped['Symbol'] = relationship(back_populates='prices')


class FilingFact(Base):
    __tablename__ = 'filing_facts'
    __table_args__ = (
        UniqueConstraint('symbol_id', 'filing_date', 'period_end_date', name='uq_filing_facts_symbol_filing_period'),
        Index('ix_filing_facts_symbol_filing_date', 'symbol_id', 'filing_date'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    symbol_id: Mapped[int] = mapped_column(ForeignKey('symbols.id', ondelete='CASCADE'), nullable=False)
    filing_date: Mapped[date] = mapped_column(Date, nullable=False)
    period_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    market_cap: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    pe_ratio: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    pb_ratio: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    eps_ttm: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    revenue_ttm: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    net_income_ttm: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    ebitda_ttm: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    source: Mapped[str | None] = mapped_column(String(64))
    raw_payload: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    symbol: Mapped['Symbol'] = relationship(back_populates='filing_facts')


class FundamentalsSnapshotDaily(Base):
    __tablename__ = 'fundamentals_snapshot_daily'
    __table_args__ = (
        UniqueConstraint('symbol_id', 'as_of_date', name='uq_fundamentals_symbol_date'),
        Index('ix_fundamentals_symbol_date', 'symbol_id', 'as_of_date'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    symbol_id: Mapped[int] = mapped_column(ForeignKey('symbols.id', ondelete='CASCADE'), nullable=False)
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False)
    market_cap: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    pe_ratio: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    pb_ratio: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    eps_ttm: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    revenue_ttm: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    net_income_ttm: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    ebitda_ttm: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    source: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    symbol: Mapped['Symbol'] = relationship(back_populates='fundamentals')


class FactorScoreDaily(Base):
    __tablename__ = 'factor_scores_daily'
    __table_args__ = (
        UniqueConstraint('symbol_id', 'score_date', 'factor_name', name='uq_factor_scores_symbol_date_factor'),
        Index('ix_factor_scores_symbol_date', 'symbol_id', 'score_date'),
        Index('ix_factor_scores_date_factor', 'score_date', 'factor_name'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    symbol_id: Mapped[int] = mapped_column(ForeignKey('symbols.id', ondelete='CASCADE'), nullable=False)
    score_date: Mapped[date] = mapped_column(Date, nullable=False)
    factor_name: Mapped[str] = mapped_column(String(64), nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    rank_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 5))
    model_version: Mapped[str | None] = mapped_column(String(64))
    factor_metadata: Mapped[dict | None] = mapped_column('metadata', JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    symbol: Mapped['Symbol'] = relationship(back_populates='factor_scores')


class Recommendation(Base):
    __tablename__ = 'recommendations'
    __table_args__ = (
        UniqueConstraint('symbol_id', 'recommendation_date', name='uq_recommendations_symbol_date'),
        Index('ix_recommendations_symbol_date', 'symbol_id', 'recommendation_date'),
        Index('ix_recommendations_date_action', 'recommendation_date', 'action'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    symbol_id: Mapped[int] = mapped_column(ForeignKey('symbols.id', ondelete='CASCADE'), nullable=False)
    recommendation_date: Mapped[date] = mapped_column(Date, nullable=False)
    action: Mapped[RecommendationAction] = mapped_column(
        Enum(RecommendationAction, name='recommendation_action'),
        nullable=False,
    )
    conviction: Mapped[Decimal | None] = mapped_column(Numeric(6, 5))
    target_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    horizon_days: Mapped[int | None] = mapped_column(Integer)
    rationale: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    symbol: Mapped['Symbol'] = relationship(back_populates='recommendations')


class StockComment(Base):
    __tablename__ = 'stock_comments'
    __table_args__ = (
        Index('ix_stock_comments_symbol_created', 'symbol_id', 'created_at'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    symbol_id: Mapped[int] = mapped_column(ForeignKey('symbols.id', ondelete='CASCADE'), nullable=False)
    nickname: Mapped[str] = mapped_column(String(40), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    symbol: Mapped['Symbol'] = relationship(back_populates='stock_comments')
