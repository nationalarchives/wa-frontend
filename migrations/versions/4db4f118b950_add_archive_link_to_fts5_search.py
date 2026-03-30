"""add archive_link to fts5 search

Revision ID: 4db4f118b950
Revises: 2b8bd07932b2
Create Date: 2026-03-27 11:47:07.524710

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4db4f118b950"
down_revision: Union[str, Sequence[str], None] = "2b8bd07932b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop FTS5 virtual table and recreate to include the archive_link
    op.execute("DROP TABLE IF EXISTS archive_records_fts")
    op.execute("""
        CREATE VIRTUAL TABLE archive_records_fts USING fts5(
            profile_name,
            description,
            archive_link,
            content=archive_records,
            content_rowid=id
        )
    """)

    # Build FTS5 index from existing archive_records data
    op.execute("""
        INSERT INTO archive_records_fts(rowid, profile_name, description, archive_link)
        SELECT id, profile_name, description, archive_link FROM archive_records
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop FTS5 virtual table and recreate without the archive_link
    op.execute("DROP TABLE IF EXISTS archive_records_fts")
    op.execute("""
        CREATE VIRTUAL TABLE archive_records_fts USING fts5(
            profile_name,
            description,
            content=archive_records,
            content_rowid=id
        )
    """)

    # Build FTS5 index from existing archive_records data
    op.execute("""
        INSERT INTO archive_records_fts(rowid, profile_name, description)
        SELECT id, profile_name, description FROM archive_records
    """)
