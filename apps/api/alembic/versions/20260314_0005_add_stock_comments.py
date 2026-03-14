"""add stock comments table

Revision ID: 20260314_0005
Revises: 20260309_0004
Create Date: 2026-03-14 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = '20260314_0005'
down_revision = '20260309_0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'stock_comments',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('symbol_id', sa.BigInteger(), nullable=False),
        sa.Column('nickname', sa.String(length=40), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['symbol_id'], ['symbols.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_stock_comments_symbol_created', 'stock_comments', ['symbol_id', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_stock_comments_symbol_created', table_name='stock_comments')
    op.drop_table('stock_comments')
