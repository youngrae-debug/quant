# quant-engine

Reusable scoring engine package shared by API, batch jobs, and backtests.

## Features

- factor scoring: value, growth, profitability, momentum, expectation
- sector-relative percentile ranking
- final score (0-100)
- rating mapping: Strong Buy / Buy / Hold / Sell / Strong Sell
- strong buy streak calculation
- recommendation cooldown check

## Run tests

From `packages/quant-engine`:

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
```
