# ========== CONFIG ==========
COMPOSE=docker compose --env-file .env.docker -f docker-compose.yml

# ========== START / STOP ==========

# Lekki tryb (codzienna praca)
up:
	$(COMPOSE) up -d backend db redis

# Pełny stack (frontend + celery)
up-full:
	$(COMPOSE) --profile full up -d

# Stop wszystkiego
down:
	$(COMPOSE) down

# Restart (lekki - FAST)
restart:
	$(COMPOSE) up -d --build backend db redis

# Restart full stack
restart-full:
	$(COMPOSE) --profile full up -d --build

# ========== BUILD ==========

build:
	$(COMPOSE) build

# ========== LOGS ==========

logs:
	$(COMPOSE) logs -f

logs-backend:
	$(COMPOSE) logs -f backend

logs-celery:
	$(COMPOSE) logs -f celery

# ========== SHELL ==========

backend:
	$(COMPOSE) exec backend bash

frontend:
	$(COMPOSE) exec frontend sh

# ========== DJANGO ==========

migrate:
	$(COMPOSE) exec backend python manage.py migrate

makemigrations:
	$(COMPOSE) exec backend python manage.py makemigrations

collectstatic:
	$(COMPOSE) exec backend python manage.py collectstatic --noinput

createsuperuser:
	$(COMPOSE) exec backend python manage.py createsuperuser

# ========== TESTY ==========

test-backend:
	$(COMPOSE) exec backend python manage.py test

test-frontend:
	$(COMPOSE) exec frontend npm test

# ========== DEBUG ==========

ps:
	$(COMPOSE) ps

stats:
	docker stats