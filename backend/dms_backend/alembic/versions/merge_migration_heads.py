"""merge migration heads

Revision ID: merge_migration_heads
Revises: update_user_model, add_ai_fields
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'merge_migration_heads'
down_revision = ('update_user_model', 'add_ai_fields')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
