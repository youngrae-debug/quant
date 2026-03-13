# Local Development Guide

## What this project looks like

This repository is a monorepo with three parts that matter for local website development:

- `apps/api`: FastAPI backend with SQLAlchemy and Alembic.
- `apps/web`: Next.js frontend that calls the API through `NEXT_PUBLIC_API_URL`.
- `packages/collectors` and `packages/quant-engine`: data ingestion and scoring jobs that fill the database used by the API.

For local PC development, the easiest split is:

- run PostgreSQL in Docker
- run FastAPI directly on Windows through a Python virtual environment
- run Next.js directly on Windows through Node.js

That keeps the database isolated while giving you fast code reload for the API and web app.

## Prerequisites

- Windows PowerShell
- Docker Desktop
- Node.js 22.x and npm 10.x
- Python 3.11+ available through the `py` launcher

The current machine already has Node.js, npm, Docker, and `py`. The plain `python` command is not on PATH, so the local scripts use `py` and `.venv\Scripts\python.exe`.

## 1. Bootstrap the local environment

From the repository root:

```powershell
.\scripts\local\Setup-LocalDev.ps1
```

This script does four things:

1. creates local env files when they do not exist yet
2. creates `.venv`
3. installs Python packages in editable mode for `quant-engine`, `collectors`, and `apps/api`
4. runs `npm install` for the workspace

Generated local files:

- `.env`
- `apps/api/.env`
- `apps/web/.env.local`
- `packages/collectors/.env`

## 2. Start PostgreSQL locally

Make sure Docker Desktop is running first.

```powershell
.\scripts\local\Start-LocalDb.ps1
```

This starts only the `db` service from `docker-compose.yml` and waits for the `quant-db` container health check to turn green.

To stop the local database later:

```powershell
.\scripts\local\Stop-LocalDb.ps1
```

## 3. Database connection setup

The local backend uses `localhost` instead of the Docker-internal hostname `db`.

Key files:

- `apps/api/.env`
- `packages/collectors/.env`
- `apps/api/alembic.ini`

Local development default:

```env
DATABASE_URL=postgresql+psycopg://quant:quant@localhost:5432/quant
```

If you change the PostgreSQL username, password, database name, or port, update the same value in both:

- `apps/api/.env`
- `packages/collectors/.env`

## 4. Run migrations

```powershell
.\scripts\local\Invoke-Migrations.ps1
```

This applies the Alembic migrations in `apps/api/alembic/versions` to your local PostgreSQL instance.

## 5. Run the backend server

Single-command backend startup:

```powershell
.\scripts\local\Start-Backend.ps1
```

That script:

1. starts PostgreSQL if needed
2. runs migrations
3. launches FastAPI with auto-reload on `http://localhost:8000`

If you only want to run the API server without re-running migrations:

```powershell
.\scripts\local\Start-Api.ps1
```

Useful backend URLs:

- API docs: `http://localhost:8000/docs`
- health check: `http://localhost:8000/health`

## 6. Run the frontend

Open a second PowerShell window:

```powershell
.\scripts\local\Start-Web.ps1
```

The frontend reads `apps/web/.env.local` and targets:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Open `http://localhost:3000`.

## 7. Load real data for development

Without ingestion jobs, the website can load but ranking and recommendation pages may be empty.

To populate data:

```powershell
.\scripts\local\Run-DataPipeline.ps1
```

Optional example with a fixed date:

```powershell
.\scripts\local\Run-DataPipeline.ps1 -AsOfDate 2026-03-13 -PriceLimit 100
```

What this runs:

1. SEC symbol sync
2. symbol metadata sync
3. SEC filing sync
4. price sync
5. fundamentals materialization
6. quant scoring
7. recommendation refresh

Before using that pipeline, fill in API keys where needed:

- `packages/collectors/.env`
- `FINNHUB_API_KEY`
- `TWELVEDATA_API_KEY`
- `ALPHA_VANTAGE_API_KEY`
- `SEC_USER_AGENT`

## Recommended local workflow

Terminal 1:

```powershell
.\scripts\local\Start-Backend.ps1
```

Terminal 2:

```powershell
.\scripts\local\Start-Web.ps1
```

Optional one-time data load:

```powershell
.\scripts\local\Run-DataPipeline.ps1
```

## Troubleshooting

- If `.\scripts\local\Setup-LocalDev.ps1` fails at Python install, confirm `py --version` works.
- If `.\scripts\local\Start-LocalDb.ps1` fails immediately, launch Docker Desktop first and wait for the daemon to finish starting.
- If the API cannot connect to PostgreSQL, confirm `docker ps` shows `quant-db` healthy and that `DATABASE_URL` uses `localhost`.
- If the frontend loads but shows empty lists, run the data pipeline after configuring collector API keys.