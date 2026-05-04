#!/bin/sh
set -e

echo "🧠 Celery worker starting..."

exec celery -A rpg_project worker -l info --concurrency=1 --prefetch-multiplier=1  --max-memory-per-child=150000