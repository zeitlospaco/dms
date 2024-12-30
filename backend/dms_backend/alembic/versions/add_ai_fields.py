"""add AI fields to document model

Revision ID: add_ai_fields
Revises: 
Create Date: 2024-01-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_ai_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add extracted_text and confidence_score columns to documents table
    op.add_column('documents', sa.Column('extracted_text', sa.String(), nullable=True))
    op.add_column('documents', sa.Column('confidence_score', sa.Float(), nullable=True))


def downgrade() -> None:
    # Remove the new columns
    op.drop_column('documents', 'extracted_text')
    op.drop_column('documents', 'confidence_score')
