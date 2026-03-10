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


## Fallback provider 사용 방법

1. `.env`에 기본/보조 공급자 키를 설정합니다.

```env
FINNHUB_API_KEY=your_finnhub_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
POLYGON_API_KEY=your_polygon_key
TWELVEDATA_API_KEY=your_twelvedata_key
# 순서대로 fallback 시도
PRICE_FALLBACK_PROVIDERS=alphavantage,polygon,twelvedata,yfinance,stooq
```

2. 가격 동기화 실행

```bash
python -m collectors.jobs sync-prices --max-symbols 50
```

3. 동작 방식
- Finnhub가 정상 응답하면 `source='finnhub'`로 저장됩니다.
- Finnhub가 `403` 또는 `no candles`이면 `PRICE_FALLBACK_PROVIDERS` 순서대로 시도합니다.
- 각 provider가 성공하면 해당 `source` 값(`alpha_vantage`, `polygon`, `twelvedata`, `yfinance`, `stooq`)으로 저장됩니다.

4. 결과 확인 예시

```sql
SELECT source, COUNT(*)
FROM price_daily
GROUP BY source
ORDER BY COUNT(*) DESC;
```

## Notes

- SEC calls use configurable `SEC_USER_AGENT`.
- Price sync supports retries, rate-limit backoff, and incremental sync by last loaded date.
- If Finnhub fails (403 or no candles), configurable fallback providers are used in order via `PRICE_FALLBACK_PROVIDERS` (default: `alphavantage,polygon,twelvedata,yfinance,stooq`).
- `ALPHA_VANTAGE_API_KEY`, `POLYGON_API_KEY`, `TWELVEDATA_API_KEY` enable each provider; `yfinance` works without API key.
- Materializer enforces point-in-time logic by using only facts with `filing_date <= as_of_date`.
