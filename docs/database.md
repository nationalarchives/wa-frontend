# Database

The application uses a local SQLite database (by default) to store archive records. This allows the A-to-Z archive pages to be served without relying on the Wagtail API for every request.

In production, the database URI can be overridden via the `SQLALCHEMY_DATABASE_URI` environment variable to use a different database backend supported by SQLAlchemy.

## Setup

Migrations are applied automatically on container startup via `docker-entrypoint.sh`. To run them manually:

```sh
docker compose exec app poetry run alembic upgrade head
```

## Migrations

To create a new migration after changing a model:

```sh
docker compose exec app poetry run alembic revision --autogenerate -m "describe your change"
```

Review the generated file in `migrations/versions/` before applying it.

## Schema

### `archive_records`

Stores archive entries synced from the external JSON feed.

| Column                   | Type             | Description                                             |
| ------------------------ | ---------------- | ------------------------------------------------------- |
| `id`                     | Integer (PK)     | Auto-incrementing primary key                           |
| `wam_id`                 | Integer          | Unique identifier from the source data                  |
| `profile_name`           | Text             | Display name of the archived site                       |
| `record_url`             | Text             | URL of the original site                                |
| `archive_link`           | Text             | URL of the archived version                             |
| `domain_type`            | String           | Type of domain (e.g. Central government)                |
| `first_capture_display`  | String           | Human-readable first capture date                       |
| `latest_capture_display` | String           | Human-readable latest capture date                      |
| `ongoing`                | Boolean          | Whether the site is still being archived                |
| `description`            | Text             | Description of the archived site                        |
| `sort_name`              | Text (indexed)   | Normalised name for sorting (strips leading "The ")     |
| `first_character`        | String (indexed) | First character for A-to-Z filtering (`a`-`z` or `0-9`) |
| `record_hash`            | String (indexed) | MD5 hash of record data used for change detection       |
| `created_at`             | DateTime         | Record creation timestamp                               |
| `updated_at`             | DateTime         | Record last updated timestamp                           |

## Configuration

| Variable                  | Default            | Description             |
| ------------------------- | ------------------ | ----------------------- |
| `SQLALCHEMY_DATABASE_URI` | `sqlite:///app.db` | Database connection URI |
