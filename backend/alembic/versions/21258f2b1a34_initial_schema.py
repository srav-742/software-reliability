"""Initial Schema

Revision ID: 21258f2b1a34
Revises: f548ce7897eb
Create Date: 2026-07-09 10:35:37.399494

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '21258f2b1a34'
down_revision: Union[str, Sequence[str], None] = 'f548ce7897eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
