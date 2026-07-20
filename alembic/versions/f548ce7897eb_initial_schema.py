"""Initial Schema

Revision ID: f548ce7897eb
Revises: f89e52ae0484
Create Date: 2026-07-08 20:43:42.505963

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f548ce7897eb'
down_revision: Union[str, Sequence[str], None] = 'f89e52ae0484'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
