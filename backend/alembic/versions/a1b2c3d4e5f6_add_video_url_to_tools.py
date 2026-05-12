"""add video_url to tools

Revision ID: a1b2c3d4e5f6
Revises: daf0779dfb50
Create Date: 2026-05-12 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'daf0779dfb50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tools', sa.Column('video_url', sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column('tools', 'video_url')
