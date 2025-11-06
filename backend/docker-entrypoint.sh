#!/bin/bash
# Entrypoint script that can run either uvicorn or celery based on environment variable

if [ "$CELERY_WORKER" = "true" ]; then
    echo "Starting Celery worker..."
    exec celery -A app.core.celery_app worker --loglevel=info
else
    echo "Starting FastAPI server..."
    exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
fi

