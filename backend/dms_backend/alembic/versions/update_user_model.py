"""update user model

Revision ID: update_user_model
Revises: add_ai_fields
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'update_user_model'
down_revision = 'add_ai_fields'
branch_labels = None
depends_on = None

def upgrade():
    # Create new users table
    op.create_table('users_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=True),
        sa.Column('credentials', sa.JSON(), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_new_email', 'users_new', ['email'], unique=True)
    op.create_index('ix_users_new_id', 'users_new', ['id'], unique=False)

    # Copy data from old table
    op.execute('''
        INSERT INTO users_new (id, email, hashed_password, created_at)
        SELECT id, email, hashed_password, created_at
        FROM users
    ''')

    # Drop old table and rename new one
    op.drop_table('users')
    op.rename_table('users_new', 'users')

def downgrade():
    # Create old users table
    op.create_table('users_old',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_old_email', 'users_old', ['email'], unique=True)
    op.create_index('ix_users_old_id', 'users_old', ['id'], unique=False)

    # Copy data back
    op.execute('''
        INSERT INTO users_old (id, email, hashed_password, created_at)
        SELECT id, email, hashed_password, created_at
        FROM users
    ''')

    # Drop new table and rename old one back
    op.drop_table('users')
    op.rename_table('users_old', 'users')
