import re

from app.lib import database
from app.lib.cache import cache
from app.lib.models import ArchiveRecord
from app.lib.util import ARCHIVE_SEARCH_MAX_LENGTH
from flask import current_app
from sqlalchemy import func, text
from sqlalchemy.exc import OperationalError


@cache.cached(timeout=0, key_prefix="archive:characters")
def get_available_characters():
    """
    Get list of characters that have archive records.

    Returns:
        list: Sorted list of unique first characters (e.g., ['0-9', 'a', 'b', ...])
    """
    try:
        characters = (
            database.db_session.query(ArchiveRecord.first_character)
            .distinct()
            .order_by(ArchiveRecord.first_character)
            .all()
        )
        return [char[0] for char in characters]
    except Exception as e:
        current_app.logger.error(f"Failed to get available characters: {e}")
        raise


@cache.memoize(timeout=0)
def get_records_by_character(character):
    """
    Get archive records filtered by first character.

    Args:
        character: Character to filter by (e.g., 'a', '0-9')

    Returns:
        dict: Dictionary with 'items' (list of records) and 'meta' (pagination info)
    """
    try:
        # Build base query
        query = (
            database.db_session.query(ArchiveRecord)
            .filter(ArchiveRecord.first_character == character)
            .order_by(ArchiveRecord.sort_name)
        )

        total_count = query.count()
        records = query.all()

        # Convert to dictionaries
        items = [
            {
                "id": record.id,
                "profile_name": record.profile_name,
                "record_url": record.record_url,
                "archive_link": record.archive_link,
                "domain_type": record.domain_type,
                "first_capture_display": record.first_capture_display,
                "latest_capture_display": record.latest_capture_display,
                "ongoing": record.ongoing,
                "wam_id": record.wam_id,
                "description": record.description,
                "sort_name": record.sort_name,
                "first_character": record.first_character,
            }
            for record in records
        ]

        return {
            "items": items,
            "meta": {
                "total_count": total_count,
            },
        }
    except Exception as e:
        current_app.logger.error(
            f"Failed to get archive records for character '{character}': {e}"
        )
        raise


def get_record_count():
    """
    Get total count of archive records.

    Returns:
        int: Total number of records in database
    """
    try:
        count = database.db_session.query(func.count(ArchiveRecord.id)).scalar()
        return count or 0
    except Exception as e:
        current_app.logger.error(f"Failed to get record count: {e}")
        raise


def search_records(query):
    """
    Full-text search across archive records (profile_name and description) using FTS5.

    Args:
        query: Search string (e.g. "government digital")

    Returns:
        dict: Dictionary with 'items' (list of records) and 'meta' (count info)
    """
    sanitised_query = _sanitize_fts_query(query)

    if not sanitised_query:
        return {
            "items": [],
            "meta": {
                "total_count": 0,
            },
        }

    try:
        sql = text("""
            SELECT ar.*
            FROM archive_records ar
            INNER JOIN archive_records_fts fts ON ar.id = fts.rowid
            WHERE archive_records_fts MATCH :query
            ORDER BY rank, ar.sort_name
        """)

        result = database.db_session.execute(sql, {"query": sanitised_query})
        rows = result.fetchall()

        items = [dict(row._mapping) for row in rows]

        return {
            "items": items,
            "meta": {
                "total_count": len(items),
            },
        }
    except OperationalError:
        return {"items": [], "meta": {"total_count": 0, "error": "invalid_query"}}
    except Exception as e:
        current_app.logger.error(f"Failed to search archive records for '{query}': {e}")
        raise


def _sanitize_fts_query(query):
    """
    Remove characters and syntax patterns that would cause FTS5 query errors, keeping
    FTS5 special characters:

    - Prefix wildcard: digit* matches digital, digitisation, digitised..
    - Phrase search: "government digital"
    - Grouping with parenthesis: (health OR digital) AND service
    """
    # Truncate to prevent excessively long queries
    query = query[:ARCHIVE_SEARCH_MAX_LENGTH]

    # Strip characters not valid in FTS5 queries
    query = re.sub(r'[^\w\s"()*]', " ", query)

    # Strip leading/trailing boolean operators
    query = re.sub(r"^\s*(AND|OR|NOT)\s+", "", query, flags=re.IGNORECASE)
    query = re.sub(r"\s+(AND|OR|NOT)\s*$", "", query, flags=re.IGNORECASE)

    # Strip leading wildcards
    query = re.sub(r"(?<!\w)\*", "", query)

    # Strip unmatched quotes
    if query.count('"') % 2 != 0:
        query = query.replace('"', "")

    # Strip unbalanced parentheses
    if query.count("(") != query.count(")"):
        query = re.sub(r"[()]", "", query)

    return query.strip()
