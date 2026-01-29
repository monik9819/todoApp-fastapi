"""add_index_and_timestamps_to_todos_table

Revision ID: a3b7c9d2e4f6
Revises: 6e5a59aa84a4
Create Date: 2025-12-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3b7c9d2e4f6'
down_revision: Union[str, Sequence[str], None] = '6e5a59aa84a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add index on owner_id for faster queries
    op.create_index('ix_todos_owner_id', 'todos', ['owner_id'], unique=False)

    # Add created_at column with default value for existing rows
    op.add_column('todos', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.execute("UPDATE todos SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
    op.alter_column('todos', 'created_at', nullable=False)

    # Add updated_at column with default value for existing rows
    op.add_column('todos', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.execute("UPDATE todos SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")
    op.alter_column('todos', 'updated_at', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove timestamps
    op.drop_column('todos', 'updated_at')
    op.drop_column('todos', 'created_at')

    # Remove index
    op.drop_index('ix_todos_owner_id', table_name='todos')
