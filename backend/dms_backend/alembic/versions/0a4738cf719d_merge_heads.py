"""merge heads

Revision ID: 0a4738cf719d
Revises: a4b325debba9, add_credentials_column
Create Date: 2025-01-08 11:13:47.390062

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a4738cf719d'
down_revision: Union[str, None] = ('a4b325debba9', 'add_credentials_column')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
