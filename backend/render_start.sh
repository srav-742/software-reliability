#!/usr/bin/env bash
# Render start script for the backend service.
# Render clones the entire repo, so we need to cd into the backend directory
# before running alembic migrations and starting the uvicorn server.

set -e

cd backend

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting Uvicorn server..."
uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
