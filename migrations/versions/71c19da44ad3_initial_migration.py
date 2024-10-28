"""Initial migration

Revision ID: 71c19da44ad3
Revises: f66fd6aff91b
Create Date: 2024-10-25 23:32:12.472291

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71c19da44ad3'
down_revision: Union[str, None] = 'f66fd6aff91b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
