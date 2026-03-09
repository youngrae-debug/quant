# Quant Monorepo (Scaffold - Phase 1)

Production-oriented monorepo scaffold for an investment research platform.

## Included in this phase

- `apps/web`: Next.js 15 + TypeScript + Tailwind skeleton.
- `apps/api`: FastAPI + SQLAlchemy + Alembic skeleton.
- `packages/quant-engine`: Python package scaffold for factor scoring.
- `packages/collectors`: Python package scaffold for SEC and Finnhub collectors.
- `packages/db`: Placeholder for schema assets.
- PostgreSQL + API + Web services via Docker Compose.
- Healthchecks for `db`, `api`, and `web` services in Docker Compose.
- `.env.example` files for root and packages/apps.
- `Makefile` bootstrap and container workflow helpers.

## Repository layout

```text
quant/
  apps/
    web/
    api/
  packages/
    quant-engine/
    db/
    collectors/
  infra/
    nginx/
    docker/
    scripts/
  docs/
```

## Quick start

1. Bootstrap local env files:

   ```bash
   make bootstrap
   ```

2. Start local stack:

   ```bash
   make up
   ```

3. Access services:

   - Web: http://localhost:3000
   - API docs: http://localhost:8000/docs
   - API health: http://localhost:8000/health
   - Postgres: localhost:5432

4. Verify homepage integration:

   - Open Web homepage and confirm it displays `API health status: ok`.

5. Stop services:

   ```bash
   make down
   ```

## Notes

This is intentionally scaffold-focused. Domain models, richer migrations, authentication, data ingestion workflows, and production deployment manifests will be added incrementally in later phases.
