"""add page_views table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-12 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'page_views',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('ip', sa.String(length=64), nullable=False),
        sa.Column('path', sa.String(length=512), nullable=False),
        sa.Column('method', sa.String(length=8), nullable=False, server_default='GET'),
        sa.Column('status_code', sa.Integer(), nullable=False, server_default='200'),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('user_agent', sa.String(length=512), nullable=True),
        sa.Column('referer', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_page_views_ip', 'page_views', ['ip'])
    op.create_index('ix_page_views_path', 'page_views', ['path'])
    op.create_index('ix_page_views_created_at', 'page_views', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_page_views_created_at', table_name='page_views')
    op.drop_index('ix_page_views_path', table_name='page_views')
    op.drop_index('ix_page_views_ip', table_name='page_views')
    op.drop_table('page_views')
