"""create filing facts table

Revision ID: 20260309_0003
Revises: 20260309_0002
Create Date: 2026-03-09 06:45:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '20260309_0003'
down_revision = '20260309_0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'filing_facts',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('symbol_id', sa.BigInteger(), sa.ForeignKey('symbols.id', ondelete='CASCADE'), nullable=False),
        sa.Column('filing_date', sa.Date(), nullable=False),
        sa.Column('period_end_date', sa.Date(), nullable=False),
        sa.Column('market_cap', sa.Numeric(20, 2), nullable=True),
        sa.Column('pe_ratio', sa.Numeric(12, 4), nullable=True),
        sa.Column('pb_ratio', sa.Numeric(12, 4), nullable=True),
        sa.Column('eps_ttm', sa.Numeric(18, 6), nullable=True),
        sa.Column('revenue_ttm', sa.Numeric(20, 2), nullable=True),
        sa.Column('net_income_ttm', sa.Numeric(20, 2), nullable=True),
        sa.Column('ebitda_ttm', sa.Numeric(20, 2), nullable=True),
        sa.Column('source', sa.String(length=64), nullable=True),
        sa.Column('raw_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('symbol_id', 'filing_date', 'period_end_date', name='uq_filing_facts_symbol_filing_period'),
    )
    op.create_index('ix_filing_facts_symbol_filing_date', 'filing_facts', ['symbol_id', 'filing_date'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_filing_facts_symbol_filing_date', table_name='filing_facts')
    op.drop_table('filing_facts')
