# ========== CONFIG ==========
COMPOSE=docker compose --env-file .env.docker -f docker-compose.yml

.PHONY: bootstrap up up-full down restart restart-full build logs logs-backend logs-celery backend frontend migrate makemigrations collectstatic createsuperuser test-backend test-backend-debug test-frontend ps stats

# ========== START / STOP ==========
bootstrap:
	$(COMPOSE) up -d --build backend db redis

up:
	$(COMPOSE) up -d backend db redis

up-full:
	$(COMPOSE) --profile full up -d

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) up -d --build backend db redis

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
	$(COMPOSE) exec backend sh

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
	docker compose exec backend pytest -q

test-backend-debug:
	docker compose exec backend pytest -vv -s

test-frontend:
	$(COMPOSE) exec frontend npm test

# ========== DEBUG ==========
ps:
	$(COMPOSE) ps

stats:
	docker stats