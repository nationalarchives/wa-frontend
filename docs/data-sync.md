# Archive Data Sync

The archive data sync command fetches the A-to-Z archive JSON feed and syncs it to the local database. It is the primary mechanism for keeping archive records up to date.

## Prerequisites

The local database must be initialised and migrations applied before running the sync for the first time. See the [database documentation](database.md) for details.

In normal operation, migrations and the initial sync are run automatically by `docker-entrypoint.sh` on container startup.

## Commands

### `flask sync-archive-data`

Fetches the archive JSON feed, validates entries, and syncs records to the database.

```sh
docker compose exec app poetry run flask sync-archive-data
```

**Options:**

```sh
--url TEXT                    URL to fetch JSON data from (otherwise uses ARCHIVE_JSON_URL env var)
--dry-run                     Validate and report without saving to database
--validation-batch-size INT   Number of entries to validate at once before saving (default: 5000)
--commit-batch-size INT       Number of entries per database transaction (default: 1000)
```

**Examples:**

```sh
# Sync using the ARCHIVE_JSON_URL environment variable
docker compose exec app poetry run flask sync-archive-data

# Sync from a specific URL
docker compose exec app poetry run flask sync-archive-data --url https://example.com/data.json

# Dry run - validate without saving
docker compose exec app poetry run flask sync-archive-data --dry-run

# Custom batch sizes for large datasets
docker compose exec app poetry run flask sync-archive-data --validation-batch-size 10000 --commit-batch-size 500
```

### `flask clear-archive-cache`

Clears the archive data cache without running a full sync. Useful if data gets into a bad state.

```sh
docker compose exec app poetry run flask clear-archive-cache
```

## How it works

1. **Fetch** - Downloads the full JSON dataset from the source URL
2. **Validate** - Processes entries in batches using Pydantic, computing a hash and sort fields for each entry
3. **Save** - Saves validated entries to the database in commit batches, using hash-based change detection to skip unchanged records
4. **Delete** - Removes any database records whose `wam_id` is no longer present in the source
5. **Clear cache** - Clears the archive service cache so the updated data is served immediately

## Change detection

Each record is hashed on ingest. On subsequent syncs, if the hash of an incoming entry matches the stored hash the record is skipped, avoiding unnecessary database writes. The sync summary reports how many records were created, updated, and skipped.

## Memory usage

The full JSON dataset is loaded into memory before processing begins.

Memory spikes during the initial JSON load then remains flat during batch processing.

## Environment variables

| Variable           | Description                                                              |
| ------------------ | ------------------------------------------------------------------------ |
| `ARCHIVE_JSON_URL` | Default URL for the archive JSON feed, used when `--url` is not provided |

Set `ARCHIVE_JSON_URL` in your `docker-compose.override.yml` for local development:

```yaml
services:
  app:
    environment:
      - ARCHIVE_JSON_URL=https://example.com/archive-data.json
```

In production and staging environments, `ARCHIVE_JSON_URL` should be set as an environment variable in the deployment configuration (e.g. ECS task definition, Kubernetes secret, or equivalent).
