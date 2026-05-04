#!/bin/sh
set -e

echo "🚀 Backend starting..."
export PYTHONUNBUFFERED=1
export DJANGO_SETTINGS_MODULE=rpg_project.settings

DB_HOST="${DB_HOST:-db}"
DB_NAME="${POSTGRES_DB:-django_rpg}"
DB_USER="${POSTGRES_USER:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_PASSWORD="${POSTGRES_PASSWORD:-postgres}"

export PGPASSWORD="$DB_PASSWORD"

echo "⏳ Waiting for Postgres..."

# safety timeout (żeby nie wisiało w nieskończoność)
MAX_RETRIES=30
COUNT=0

until pg_isready \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" >/dev/null 2>&1
do
  COUNT=$((COUNT+1))

  echo "Postgres not ready... ($COUNT/$MAX_RETRIES)"

  if [ "$COUNT" -ge "$MAX_RETRIES" ]; then
    echo "❌ Timeout waiting for Postgres"
    exit 1
  fi

  sleep 2
done

echo "✅ Database ready"

echo "📦 Running migrations..."
python manage.py migrate --noinput

echo "📦 Collecting static..."
python manage.py collectstatic --noinput

echo "🚀 Starting ASGI server (Daphne)..."

exec daphne -b 0.0.0.0 -p 8000 rpg_project.asgi:application