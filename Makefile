# Start kontenerów w tle
up:
	docker compose --env-file .env.development -f docker-compose.yml up -d

# Zatrzymanie kontenerów
down:
	docker compose down

# Budowanie kontenerów
build:
	COMPOSE_BAKE=true docker compose build

# Podgląd logów na żywo
logs:
	docker compose logs -f

# Restart projektu - zatrzymaj, zbuduj, uruchom, pokaż logi
restart:
	docker compose down
	COMPOSE_BAKE=true docker compose build
	docker compose up -d
	docker compose logs -f

# Wejście do kontenera backend (Django)
backend:
	docker compose exec backend bash

# Wejście do kontenera frontend (React)
frontend:
	docker compose exec frontend sh

# Migracje Django
migrate:
	docker compose exec backend python manage.py migrate

# Generowanie migracji Django
makemigrations:
	docker compose exec backend python manage.py makemigrations

# Zbieranie staticfiles Django
collectstatic:
	docker compose exec backend python manage.py collectstatic --noinput

# Tworzenie superusera Django
createsuperuser:
	docker compose exec backend python manage.py createsuperuser

# Testowanie backendu (Django)
test-backend:
	docker compose exec backend python manage.py test

# Testowanie frontendu (React)
test-frontend:
	docker compose exec frontend npm test

# Podgląd statusu kontenerów
ps:
	docker compose ps
