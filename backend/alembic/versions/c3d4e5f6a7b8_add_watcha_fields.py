"""add watcha source fields to tools and create external_reviews

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-05-17 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tool 新增来源字段
    op.add_column('tools', sa.Column('source', sa.String(32), nullable=False, server_default='manual'))
    op.add_column('tools', sa.Column('external_id', sa.String(64), nullable=True))
    op.add_column('tools', sa.Column('external_slug', sa.String(128), nullable=True))
    op.create_index('ix_tools_source', 'tools', ['source'])
    op.create_index('ix_tools_external_id', 'tools', ['external_id'])

    # 外部评论表
    op.create_table(
        'external_reviews',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('tool_id', sa.BigInteger(), nullable=False),
        sa.Column('source', sa.String(32), nullable=False, server_default='watcha'),
        sa.Column('external_id', sa.String(64), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('score', sa.Numeric(4, 2), nullable=True),
        sa.Column('author_name', sa.String(128), nullable=True),
        sa.Column('author_avatar', sa.String(512), nullable=True),
        sa.Column('upvotes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reply_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('external_created_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['tool_id'], ['tools.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_external_reviews_tool_id', 'external_reviews', ['tool_id'])
    op.create_index('ix_external_reviews_source', 'external_reviews', ['source'])
    op.create_index('ix_external_reviews_external_id', 'external_reviews', ['external_id'])


def downgrade() -> None:
    op.drop_index('ix_external_reviews_external_id', table_name='external_reviews')
    op.drop_index('ix_external_reviews_source', table_name='external_reviews')
    op.drop_index('ix_external_reviews_tool_id', table_name='external_reviews')
    op.drop_table('external_reviews')
    op.drop_index('ix_tools_external_id', table_name='tools')
    op.drop_index('ix_tools_source', table_name='tools')
    op.drop_column('tools', 'external_slug')
    op.drop_column('tools', 'external_id')
    op.drop_column('tools', 'source')
