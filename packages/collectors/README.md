# quant-collectors

Collectors for SEC symbol sync, Finnhub daily prices, and point-in-time fundamentals materialization.

## Jobs

Run from `packages/collectors`:

```bash
python -m collectors.jobs sync-sec-symbols
python -m collectors.jobs sync-prices
python -m collectors.jobs materialize-fundamentals --as-of-date 2026-03-09
```

## Sequence (phase 4)

1. `sync-sec-symbols`
2. `sync-prices`
3. filings/companyfacts ingestion (next incremental step)
4. earnings/sentiment ingestion (next incremental step)
5. `materialize-fundamentals`
6. factor scoring (next incremental step)

## Notes

- SEC calls use configurable `SEC_USER_AGENT`.
- Price sync supports retries, rate-limit backoff, and incremental sync by last loaded date.
- Materializer enforces point-in-time logic by using only facts with `filing_date <= as_of_date`.
