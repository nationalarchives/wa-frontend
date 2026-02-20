from app.lib import database
from app.lib.cache import cache
from app.lib.models import ArchiveRecord
from flask import current_app
from sqlalchemy import func


@cache.cached(timeout=3600, key_prefix="archive:characters")
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
