#!/bin/sh
set -e

echo "⏱ Celery beat starting..."

exec celery -A rpg_project beat -l info