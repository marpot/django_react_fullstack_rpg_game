SHELL := /bin/sh

DEV_ENV ?= .env.docker
PROD_ENV ?= .env.prod
COMPOSE = docker compose $(if $(wildcard $(DEV_ENV)),--env-file $(DEV_ENV),) -f docker-compose.yml
PROD_COMPOSE = docker compose --env-file $(PROD_ENV) -f docker-compose.prod.yml
DEV_SERVICES := db redis backend

.PHONY: bootstrap up down restart build ps stats frontend frontend-install \
	logs logs-backend migrate makemigrations collectstatic createsuperuser \
	logs-celery test test-backend test-backend-debug test-frontend backend up-full \
	prod-build prod-up prod-down prod-logs check-prod-env reset-dev-data

bootstrap:
	@test -f $(DEV_ENV) || cp .env.example $(DEV_ENV)
	$(COMPOSE) up -d --build $(DEV_SERVICES)

up:
	$(COMPOSE) up -d $(DEV_SERVICES)

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart $(DEV_SERVICES)

build:
	$(COMPOSE) build backend

ps:
	$(COMPOSE) ps

stats:
	@container_ids="$$($(COMPOSE) ps -q $(DEV_SERVICES))"; \
	if [ -n "$$container_ids" ]; then docker stats --no-stream $$container_ids; else echo "Development stack is not running."; fi

frontend:
	cd frontend && npm run dev

frontend-install:
	cd frontend && npm ci

logs:
	$(COMPOSE) logs -f

logs-backend:
	$(COMPOSE) logs -f backend

logs-celery:
	$(COMPOSE) --profile full logs -f celery celery-beat

backend:
	$(COMPOSE) exec backend sh

migrate:
	$(COMPOSE) exec backend python manage.py migrate

makemigrations:
	$(COMPOSE) exec backend python manage.py makemigrations

collectstatic:
	$(COMPOSE) exec backend python manage.py collectstatic --noinput

createsuperuser:
	$(COMPOSE) exec backend python manage.py createsuperuser

test: test-backend test-frontend

test-backend:
	$(COMPOSE) up -d db redis
	$(COMPOSE) run --rm backend pytest -q

test-backend-debug:
	$(COMPOSE) up -d db redis
	$(COMPOSE) run --rm backend pytest -vv -s

test-frontend:
	cd frontend && npm test -- --runInBand

up-full:
	$(COMPOSE) --profile full up -d --build $(DEV_SERVICES) celery celery-beat

check-prod-env:
	@test -f $(PROD_ENV) || { echo "Missing $(PROD_ENV). Copy .env.prod.example and set production values." >&2; exit 1; }

prod-build: check-prod-env
	$(PROD_COMPOSE) build

prod-up: check-prod-env
	$(PROD_COMPOSE) up -d

prod-down: check-prod-env
	$(PROD_COMPOSE) down

prod-logs: check-prod-env
	$(PROD_COMPOSE) logs -f

reset-dev-data:
	@printf "This removes only django_rpg_dev containers and the django_rpg_db_data volume. Continue? [y/N] "; \
	read answer; test "$$answer" = y || test "$$answer" = Y
	$(COMPOSE) down --volumes
