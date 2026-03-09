"""create core research tables

Revision ID: 20260309_0001
Revises: 
Create Date: 2026-03-09 06:10:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260309_0001'
down_revision = None
branch_labels = None
depends_on = None


recommendation_action = sa.Enum('buy', 'hold', 'sell', name='recommendation_action')


def upgrade() -> None:
    recommendation_action.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'symbols',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('ticker', sa.String(length=16), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('exchange', sa.String(length=64), nullable=True),
        sa.Column('sector', sa.String(length=128), nullable=True),
        sa.Column('industry', sa.String(length=128), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('ticker', name='uq_symbols_ticker'),
    )
    op.create_index('ix_symbols_ticker', 'symbols', ['ticker'], unique=True)

    op.create_table(
        'price_daily',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('symbol_id', sa.BigInteger(), sa.ForeignKey('symbols.id', ondelete='CASCADE'), nullable=False),
        sa.Column('price_date', sa.Date(), nullable=False),
        sa.Column('open', sa.Numeric(18, 6), nullable=True),
        sa.Column('high', sa.Numeric(18, 6), nullable=True),
        sa.Column('low', sa.Numeric(18, 6), nullable=True),
        sa.Column('close', sa.Numeric(18, 6), nullable=True),
        sa.Column('adjusted_close', sa.Numeric(18, 6), nullable=True),
        sa.Column('volume', sa.BigInteger(), nullable=True),
        sa.Column('source', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('symbol_id', 'price_date', name='uq_price_daily_symbol_date'),
    )
    op.create_index('ix_price_daily_symbol_date', 'price_daily', ['symbol_id', 'price_date'], unique=False)

    op.create_table(
        'fundamentals_snapshot_daily',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('symbol_id', sa.BigInteger(), sa.ForeignKey('symbols.id', ondelete='CASCADE'), nullable=False),
        sa.Column('as_of_date', sa.Date(), nullable=False),
        sa.Column('market_cap', sa.Numeric(20, 2), nullable=True),
        sa.Column('pe_ratio', sa.Numeric(12, 4), nullable=True),
        sa.Column('pb_ratio', sa.Numeric(12, 4), nullable=True),
        sa.Column('eps_ttm', sa.Numeric(18, 6), nullable=True),
        sa.Column('revenue_ttm', sa.Numeric(20, 2), nullable=True),
        sa.Column('net_income_ttm', sa.Numeric(20, 2), nullable=True),
        sa.Column('ebitda_ttm', sa.Numeric(20, 2), nullable=True),
        sa.Column('source', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('symbol_id', 'as_of_date', name='uq_fundamentals_symbol_date'),
    )
    op.create_index('ix_fundamentals_symbol_date', 'fundamentals_snapshot_daily', ['symbol_id', 'as_of_date'], unique=False)

    op.create_table(
        'factor_scores_daily',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('symbol_id', sa.BigInteger(), sa.ForeignKey('symbols.id', ondelete='CASCADE'), nullable=False),
        sa.Column('score_date', sa.Date(), nullable=False),
        sa.Column('factor_name', sa.String(length=64), nullable=False),
        sa.Column('score', sa.Numeric(12, 6), nullable=False),
        sa.Column('rank_pct', sa.Numeric(6, 5), nullable=True),
        sa.Column('model_version', sa.String(length=64), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('symbol_id', 'score_date', 'factor_name', name='uq_factor_scores_symbol_date_factor'),
    )
    op.create_index('ix_factor_scores_symbol_date', 'factor_scores_daily', ['symbol_id', 'score_date'], unique=False)
    op.create_index('ix_factor_scores_date_factor', 'factor_scores_daily', ['score_date', 'factor_name'], unique=False)

    op.create_table(
        'recommendations',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('symbol_id', sa.BigInteger(), sa.ForeignKey('symbols.id', ondelete='CASCADE'), nullable=False),
        sa.Column('recommendation_date', sa.Date(), nullable=False),
        sa.Column('action', recommendation_action, nullable=False),
        sa.Column('conviction', sa.Numeric(6, 5), nullable=True),
        sa.Column('target_price', sa.Numeric(18, 6), nullable=True),
        sa.Column('horizon_days', sa.Integer(), nullable=True),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_recommendations_symbol_date', 'recommendations', ['symbol_id', 'recommendation_date'], unique=False)
    op.create_index('ix_recommendations_date_action', 'recommendations', ['recommendation_date', 'action'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_recommendations_date_action', table_name='recommendations')
    op.drop_index('ix_recommendations_symbol_date', table_name='recommendations')
    op.drop_table('recommendations')

    op.drop_index('ix_factor_scores_date_factor', table_name='factor_scores_daily')
    op.drop_index('ix_factor_scores_symbol_date', table_name='factor_scores_daily')
    op.drop_table('factor_scores_daily')

    op.drop_index('ix_fundamentals_symbol_date', table_name='fundamentals_snapshot_daily')
    op.drop_table('fundamentals_snapshot_daily')

    op.drop_index('ix_price_daily_symbol_date', table_name='price_daily')
    op.drop_table('price_daily')

    op.drop_index('ix_symbols_ticker', table_name='symbols')
    op.drop_table('symbols')

    recommendation_action.drop(op.get_bind(), checkfirst=True)
