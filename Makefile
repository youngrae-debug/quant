SHELL := /bin/bash

.PHONY: bootstrap up down logs api-shell db-shell

bootstrap:
	./infra/scripts/bootstrap.sh

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

api-shell:
	docker compose exec api bash

db-shell:
	docker compose exec db psql -U $$POSTGRES_USER -d $$POSTGRES_DB
