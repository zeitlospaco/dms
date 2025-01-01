"""add version control tables

Revision ID: a5b325debba9
Revises: add_ai_fields
Create Date: 2024-02-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5b325debba9'
down_revision = 'add_ai_fields'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'document_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('comment', sa.String(), nullable=True),
        sa.Column('file_content', sa.LargeBinary(), nullable=False),
        sa.Column('metadata', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_versions_document_id'), 'document_versions', ['document_id'], unique=False)
    op.create_index(op.f('ix_document_versions_id'), 'document_versions', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_document_versions_id'), table_name='document_versions')
    op.drop_index(op.f('ix_document_versions_document_id'), table_name='document_versions')
    op.drop_table('document_versions')
