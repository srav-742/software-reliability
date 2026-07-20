"""Initial Tables

Revision ID: 7babab558b33
Revises: 8f59ec2f0d84
Create Date: 2026-07-08 20:19:14.515056

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7babab558b33'
down_revision: Union[str, Sequence[str], None] = '8f59ec2f0d84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
