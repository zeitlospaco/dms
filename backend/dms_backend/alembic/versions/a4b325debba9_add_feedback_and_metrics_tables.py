"""add_feedback_and_metrics_tables

Revision ID: a4b325debba9
Revises: 4d6522417e25
Create Date: 2024-12-30 17:41:34.054057

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4b325debba9'
down_revision: Union[str, None] = '4d6522417e25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
