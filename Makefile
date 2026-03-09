SHELL := /bin/bash

.PHONY: bootstrap up down logs api-shell db-shell cron-install cron-run-once

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

cron-install:
	crontab infra/scripts/cron.daily

cron-run-once:
	./infra/scripts/cron_symbol_sync.sh && \
	./infra/scripts/cron_filing_sync.sh && \
	./infra/scripts/cron_price_sync.sh && \
	./infra/scripts/cron_materializer.sh && \
	./infra/scripts/cron_scoring.sh && \
	./infra/scripts/cron_recommendation_refresh.sh
