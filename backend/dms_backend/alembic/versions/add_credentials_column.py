"""Add credentials column to users table

Revision ID: add_credentials_column
Revises: c715aea142e3
Create Date: 2024-01-08 11:05:44.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_credentials_column'
down_revision = 'c715aea142e3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('credentials', sa.String(), nullable=True))


def downgrade():
    op.drop_column('users', 'credentials')
