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
    # Create model_metrics table
    op.create_table(
        'model_metrics',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('precision', sa.Float(), nullable=True),
        sa.Column('recall', sa.Float(), nullable=True),
        sa.Column('f1_score', sa.Float(), nullable=True),
        sa.Column('training_size', sa.Integer(), nullable=True),
        sa.Column('validation_size', sa.Integer(), nullable=True)
    )

    # Create feedback table
    op.create_table(
        'feedback',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('correct_category', sa.String(), nullable=False),
        sa.Column('original_category', sa.String(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('comment', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('processed', sa.Boolean(), default=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )

    # Add new columns to documents table
    op.add_column('documents', sa.Column('ai_prediction', sa.String(), nullable=True))
    op.add_column('documents', sa.Column('prediction_timestamp', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove new columns from documents table
    op.drop_column('documents', 'prediction_timestamp')
    op.drop_column('documents', 'ai_prediction')

    # Drop feedback table
    op.drop_table('feedback')

    # Drop model_metrics table
    op.drop_table('model_metrics')
