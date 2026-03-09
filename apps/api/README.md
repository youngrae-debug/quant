# quant-api

FastAPI service scaffold for local development.

## Database migrations

Run migrations from `apps/api`:

```bash
alembic upgrade head
```

Generate a new migration (later phases):

```bash
alembic revision --autogenerate -m "describe change"
```
