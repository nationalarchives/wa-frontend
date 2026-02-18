#!/bin/bash
set -e

echo "Running database migrations..."
poetry run alembic upgrade head

echo "Starting application..."
exec "$@"
