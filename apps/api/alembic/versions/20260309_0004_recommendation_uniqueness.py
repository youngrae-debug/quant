"""add recommendation uniqueness

Revision ID: 20260309_0004
Revises: 20260309_0003
Create Date: 2026-03-09 06:50:00

"""
from alembic import op


revision = '20260309_0004'
down_revision = '20260309_0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint('uq_recommendations_symbol_date', 'recommendations', ['symbol_id', 'recommendation_date'])


def downgrade() -> None:
    op.drop_constraint('uq_recommendations_symbol_date', 'recommendations', type_='unique')
