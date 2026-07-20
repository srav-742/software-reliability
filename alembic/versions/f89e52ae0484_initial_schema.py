"""Initial Schema

Revision ID: f89e52ae0484
Revises: 27b22feb10ef
Create Date: 2026-07-08 20:43:16.730376

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f89e52ae0484'
down_revision: Union[str, Sequence[str], None] = '27b22feb10ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
