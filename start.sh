#!/bin/bash

# 1. Start Celery in the background (&)
# We use --concurrency=2 to save RAM on the free tier
celery -A tasks.celery_app worker --loglevel=info --concurrency=2 &

# 2. Start Gunicorn in the foreground
# This keeps the container alive and listening on the port
gunicorn app:app