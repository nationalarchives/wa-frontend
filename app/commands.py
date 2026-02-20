"""
Flask CLI command to sync archive data from external JSON source.

- Processes records in batches
- Assumes wam_id is unique
- Full JSON dataset remains in memory throughout processing
- Memory usage spikes during JSON load, but then remains flat during batch processing

Expected Schema of input:
    [
        {
            "profileName": str,
            "entryUrl": str,
            "archiveLink": str,
            "domainType": str,
            "firstCapture": str,
            "firstCaptureDisplay": str,
            "latestCapture": str,
            "latestCaptureDisplay": str,
            "ongoing": bool,
            "wamId": int,
            "wamLink": str,
            "parentId": int | None,
            "generatedOn": str,
            "currentDepartments": list,
            "previousDepartments": list,
            "description": str
        },
        {...}
    ]

Saved fields:
    [
        "profileName": str,
        "entryUrl": str,
        "archiveLink": str,
        "domainType": str,
        "firstCaptureDisplay": str,
        "latestCaptureDisplay": str,
        "ongoing": bool,
        "wamId": int,
        "description": str
    ]

Usage:
    flask sync-archive-data --url https://example.com/data.json
    flask sync-archive-data  # Uses ARCHIVE_JSON_URL environment variable
    flask sync-archive-data --dry-run  # Processes all entries without saving to database
"""

import json
import logging
import os

import click
import requests
from app.lib import database
from app.lib.archive_service import get_records_by_character
from app.lib.cache import cache
from app.lib.models import ArchiveRecord
from app.lib.schemas import ArchiveRecordSchema
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


@click.command("clear-archive-cache")
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Validate and report without saving to database",
)
def clear_archive_cache(dry_run: bool):
    _clear_cache(dry_run)


@click.command("sync-archive-data")
@click.option(
    "--url",
    type=str,
    help="URL to fetch JSON data from (otherwise uses ARCHIVE_JSON_URL env var)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Validate and report without saving to database",
)
@click.option(
    "--validation-batch-size",
    type=int,
    default=5000,
    help="Number of entries to validate at once before saving (default: 5000)",
)
@click.option(
    "--commit-batch-size",
    type=int,
    default=1000,
    help="Number of entries per database transaction (default: 1000)",
)
def sync_archive_data(url, dry_run, validation_batch_size, commit_batch_size):
    """Sync archive data from external JSON source with hash-based change detection"""

    stats = {
        "total": 0,
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "deleted": 0,
        "validation_errors": 0,
        "database_errors": 0,
    }

    url = url or os.environ.get("ARCHIVE_JSON_URL")
    if not url:
        click.secho(
            "No data source specified. Use --url or set ARCHIVE_JSON_URL environment variable",
            fg="red",
        )
        return

    # Load JSON data
    try:
        raw_data = load_data(url)
    except (requests.RequestException, json.JSONDecodeError, ValueError) as e:
        logger.error("Failed to load archive data from %s: %s", url, str(e))
        click.secho(f"Failed to load data: {e}", fg="red")
        return

    stats["total"] = len(raw_data)

    logger.info(
        "Starting archive data sync: %s entries, dry_run=%s",
        stats["total"],
        dry_run,
    )

    # Processing mode message
    mode = "DRY RUN - no changes will be saved" if dry_run else "LIVE"
    click.secho(f"Mode: {mode}\n", fg="yellow" if dry_run else None)
    click.echo(
        f"Processing {stats['total']} entries in batches of {validation_batch_size}...\n"
    )

    source_wam_ids = []
    total_validated = 0
    total_batches = (len(raw_data) + validation_batch_size - 1) // validation_batch_size

    # Process data in validation batches
    for batch_start in range(0, len(raw_data), validation_batch_size):
        batch_end = min(batch_start + validation_batch_size, len(raw_data))
        batch_data = raw_data[batch_start:batch_end]
        batch_num = (batch_start // validation_batch_size) + 1

        click.echo(
            f"\n--- Batch {batch_num}/{total_batches}: Validating entries {batch_start + 1}-{batch_end} ---"
        )

        # Validate batch
        validated_entries, validation_errors = validate_entries(batch_data)
        stats["validation_errors"] += validation_errors
        batch_valid_count = len(validated_entries)
        total_validated += batch_valid_count

        click.echo(f"Validated {batch_valid_count} entries")

        if batch_valid_count:
            # Collect wam_ids for deletion later
            batch_wam_ids = [entry.wam_id for entry in validated_entries]
            source_wam_ids.extend(batch_wam_ids)

            # Save batch immediately
            if not dry_run:
                click.echo(f"Saving {batch_valid_count} entries to database...")

            save_results = save_entries(
                validated_entries,
                batch_valid_count,
                commit_batch_size,
                dry_run,
            )

            # Accumulate stats
            for key in ("created", "updated", "skipped", "database_errors"):
                stats[key] += save_results[key]

    # Summary after all batches
    click.secho(
        f"\n\nValidation complete: {total_validated} valid entries",
        fg="green",
    )
    if validation_error_count := stats["validation_errors"]:
        click.secho(
            f"Skipped {validation_error_count} entries due to validation errors",
            fg="yellow",
        )

    # Delete entries not in source
    to_delete = database.db_session.query(ArchiveRecord).filter(
        ArchiveRecord.wam_id.not_in(source_wam_ids)
    )
    stats["deleted"] = delete_entries(to_delete, dry_run)

    # Clear cache after successful sync
    _clear_cache(dry_run)

    logger.info(
        "Archive data sync completed: %s total, %s created, %s updated, "
        "%s skipped, %s deleted, %s validation errors, %s database errors",
        stats["total"],
        stats["created"],
        stats["updated"],
        stats["skipped"],
        stats["deleted"],
        stats["validation_errors"],
        stats["database_errors"],
    )
    click.secho(
        "\nProcessing complete. Check logs for detailed statistics.",
        fg="green",
    )


def validate_entries(raw_data):
    """
    Validate raw JSON entries using Pydantic schema.

    Returns:
        tuple: (validated_entries, validation_error_count)
    """
    validated_entries = []
    validation_errors_count = 0

    for idx, raw_entry in enumerate(raw_data, 1):
        try:
            # Validate with Pydantic (computes hash, sort_name, first_character)
            validated = ArchiveRecordSchema(**raw_entry)
            validated_entries.append(validated)

        except ValidationError as e:
            validation_errors_count += 1
            wam_id = raw_entry.get("wamId", "unknown")

            # Format error details for readable output
            error_details = ", ".join(
                [
                    f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}"
                    for err in e.errors()
                ]
            )
            logger.warning(
                "Validation failed for entry %s (wam_id: %s): %s",
                idx,
                wam_id,
                error_details,
            )

    return validated_entries, validation_errors_count


def save_entries(validated_entries, total_valid_entries, commit_batch_size, dry_run):
    """
    Save validated entries to database in batches.

    Args:
        validated_entries: List of validated ArchiveRecordSchema objects
        total_valid_entries: Total count of validated entries (for progress indicator)
        commit_batch_size: Number of entries per database transaction
        dry_run: If True, skip database writes while running save logic

    Returns:
        dict: {
            "created": int,
            "updated": int,
            "skipped": int,
            "database_errors": int
        }
    """
    save_stats = {"created": 0, "updated": 0, "skipped": 0, "database_errors": 0}

    # Process entries in batches to commit incrementally
    for batch_start in range(0, len(validated_entries), commit_batch_size):
        batch_end = min(batch_start + commit_batch_size, len(validated_entries))
        batch = validated_entries[batch_start:batch_end]

        try:
            # Bulk load existing records for this batch (1 query instead of N queries)
            batch_wam_ids = [v.wam_id for v in batch]
            existing_records = {
                r.wam_id: r
                for r in database.db_session.query(ArchiveRecord)
                .filter(ArchiveRecord.wam_id.in_(batch_wam_ids))
                .all()
            }

            # Disable autoflush for performance (flush only on commit)
            with database.db_session.no_autoflush:
                for validated in batch:
                    result = save_entry(validated, existing_records, dry_run)
                    save_stats[result] += 1

                    processed = (
                        save_stats["created"]
                        + save_stats["updated"]
                        + save_stats["skipped"]
                    )
                    if processed % 1000 == 0:
                        click.echo(f"  Processed {processed}/{total_valid_entries}...")

            # Commit batch
            if not dry_run:
                database.db_session.commit()
                # Clear session cache to free memory
                database.db_session.expire_all()

        except SQLAlchemyError as e:
            database.db_session.rollback()
            save_stats["database_errors"] += len(batch)
            logger.error(
                "Failed to process batch %s-%s: %s", batch_start, batch_end, str(e)
            )
            click.secho(
                f"Failed to process batch {batch_start}-{batch_end}: {e}",
                fg="red",
            )

    return save_stats


def delete_entries(query, dry_run):
    """
    Delete database entries from a pre-filtered query.

    Args:
        query: SQLAlchemy query of ArchiveRecord entries to delete
        dry_run: If True, count deletions without writing to database

    Returns:
        int: Number of entries deleted (or that would be deleted in dry run), or -1 if
        deletion failed
    """
    if not dry_run:
        click.echo("\nRemoving entries not in source...")

    try:
        record_count = query.count()

        if not dry_run:
            query.delete(synchronize_session=False)
            database.db_session.commit()
            if record_count:
                click.echo(f"Deleted {record_count} entries not in source")
        return record_count
    except SQLAlchemyError as e:
        if not dry_run:
            database.db_session.rollback()
            logger.error("Database error deleting removed entries: %s", str(e))
            click.secho(f"Failed to delete removed entries: {e}", fg="red")
        return -1


def load_data(url):
    """
    Load JSON data from URL.

    Args:
        url: URL to fetch JSON data from

    Returns:
        list: Parsed JSON array of archive entries

    Raises:
        requests.RequestException: If HTTP request fails
        json.JSONDecodeError: If response is not valid JSON
    """
    click.echo(f"Fetching data from {url}...")
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.json()


def save_entry(validated: ArchiveRecordSchema, existing_records: dict, dry_run=False):
    """
    Save or update an entry in the database using hash-based change detection.

    Args:
        validated: Validated ArchiveRecordSchema object
        existing_records: Dict of {wam_id: ArchiveRecord} for lookups
        dry_run: If True, determine what would happen without writing to database

    Returns: 'created', 'updated', or 'skipped'
    """
    # Get data excluding wam_id
    data = validated.model_dump(mode="json", by_alias=False, exclude={"wam_id"})

    # Check if record exists
    existing = existing_records.get(validated.wam_id)

    if dry_run:
        if existing is None:
            return "created"
        if existing.record_hash == validated.record_hash:
            return "skipped"
        return "updated"

    if existing is None:
        # Create new record
        new_record = ArchiveRecord(wam_id=validated.wam_id, **data)
        database.db_session.add(new_record)
        return "created"

    # Check if changed (hash-based change detection)
    if existing.record_hash == validated.record_hash:
        return "skipped"

    # Update existing record
    for field, value in data.items():
        setattr(existing, field, value)

    return "updated"


def _clear_cache(dry_run: bool):
    """
    Clear the archive service cache.

    Args:
        dry_run: If True, skip cache clearing
    """
    if not dry_run:
        click.echo("\nClearing archive caches...")
        try:
            cache.delete("archive:characters")
            cache.delete_memoized(get_records_by_character)
            click.echo("Caches cleared")
        except Exception as e:
            logger.error("Failed to clear archive caches: %s", str(e))
            click.secho(f"Failed to clear caches: {e}")
