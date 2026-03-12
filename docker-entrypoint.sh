#!/bin/bash
set -e

echo "Running database migrations..."
poetry run alembic upgrade head

echo "Syncing archive data..."
poetry run flask sync-archive-data

echo "Starting application..."
exec "$@"
