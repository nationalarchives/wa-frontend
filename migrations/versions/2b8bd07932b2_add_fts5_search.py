"""add fts5 search

Revision ID: 2b8bd07932b2
Revises: 2116283378df
Create Date: 2026-03-02 15:29:41.489419

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2b8bd07932b2"
down_revision: Union[str, Sequence[str], None] = "2116283378df"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create FTS5 virtual table for search using external content table pattern
    op.execute("""
        CREATE VIRTUAL TABLE archive_records_fts USING fts5(
            profile_name,
            description,
            content=archive_records,
            content_rowid=id
        )
    """)

    # Build initial FTS5 index from existing archive_records data
    op.execute("""
        INSERT INTO archive_records_fts(rowid, profile_name, description)
        SELECT id, profile_name, description FROM archive_records
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS archive_records_fts")
