# Quant Monorepo (Scaffold - Phase 1+)

Production-oriented monorepo scaffold for an investment research platform.

## Local Windows development

For a Windows-first local setup that runs PostgreSQL in Docker and the API/Web servers directly on your PC, see [docs/local-development.md](docs/local-development.md).

For exposing only the backend to Vercel through Cloudflare Tunnel, see [docs/cloudflare-tunnel.md](docs/cloudflare-tunnel.md).

## Included

- `apps/web`: Next.js 15 + TypeScript + Tailwind frontend.
- `apps/api`: FastAPI + SQLAlchemy + Alembic backend.
- `packages/quant-engine`: shared scoring engine package.
- `packages/collectors`: SEC/Finnhub collectors and materializer jobs.
- `packages/db`: placeholder for database assets.
- PostgreSQL + API + Web services via Docker Compose.
- Healthchecks for `db`, `api`, and `web` services.
- Cron-ready batch scripts with structured JSON logs and idempotent execution.

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

4. Stop services:

   ```bash
   make down
   ```

## Batch automation (cron)

Install schedule:

```bash
make cron-install
```

Run full pipeline once:

```bash
make cron-run-once
```

Default UTC schedule in `infra/scripts/cron.daily`:

- 04:00 symbol sync
- 04:10 filing sync
- 04:30 price sync
- 05:00 materializer
- 05:30 scoring
- 06:00 recommendation refresh

Each cron wrapper script:

- emits structured JSON logs
- is idempotent per day via done markers (`var/run/jobs/*.done`)
- prevents overlapping runs via file lock (`flock`)
