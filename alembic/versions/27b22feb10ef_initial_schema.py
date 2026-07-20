"""Initial Schema

Revision ID: 27b22feb10ef
Revises: 7babab558b33
Create Date: 2026-07-08 20:38:38.885079

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27b22feb10ef'
down_revision: Union[str, Sequence[str], None] = '7babab558b33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
