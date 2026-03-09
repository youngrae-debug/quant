"""add cik and sic to symbols

Revision ID: 20260309_0002
Revises: 20260309_0001
Create Date: 2026-03-09 06:35:00

"""
from alembic import op
import sqlalchemy as sa


revision = '20260309_0002'
down_revision = '20260309_0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('symbols', sa.Column('cik', sa.String(length=10), nullable=True))
    op.add_column('symbols', sa.Column('sic', sa.String(length=8), nullable=True))
    op.create_unique_constraint('uq_symbols_cik', 'symbols', ['cik'])
    op.create_index('ix_symbols_cik', 'symbols', ['cik'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_symbols_cik', table_name='symbols')
    op.drop_constraint('uq_symbols_cik', 'symbols', type_='unique')
    op.drop_column('symbols', 'sic')
    op.drop_column('symbols', 'cik')
