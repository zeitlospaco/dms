"""merge multiple heads

Revision ID: 4d6522417e25
Revises: add_ai_fields, c715aea142e3
Create Date: 2024-12-30 17:28:01.148260

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d6522417e25'
down_revision: Union[str, None] = ('add_ai_fields', 'c715aea142e3')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
