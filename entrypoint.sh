#!/bin/bash
set -e

# Run migrations
uv run python manage.py migrate

exec "$@"
