# Price Sync 운영 체크리스트 / SQL / 테스트 템플릿

아래 내용은 `sync-prices` 실행 직후 품질을 빠르게 검증하기 위한 **즉시 적용 가능한 템플릿**입니다.

## 1) 실행 체크리스트 (운영용)

- [x] `.env`에 필수/선택 키가 운영 정책대로 설정되었는지 확인
  - `FINNHUB_API_KEY`, `ALPHA_VANTAGE_API_KEY`, `TWELVEDATA_API_KEY` (fallback용 선택)
  - `yfinance`는 기본(Primary) 소스로 키 없이 동작
  - `PRICE_FALLBACK_PROVIDERS` 순서 확인
- [x] 실행 전 스냅샷 저장
  - 총 건수(`price_daily`)
  - 최신 영업일(`max(price_date)`)
  - source 분포
- [x] `sync-prices` 실행
- [x] 실행 후 검증
  - upsert/insert/update 로그 확인
  - 최신일 기준 커버리지(활성 심볼 대비 적재 심볼 수) 확인
  - source 분포가 의도된 fallback 정책과 일치하는지 확인
- [x] 임계치 판정
  - 커버리지 < 80%: Warning
  - 커버리지 < 60%: Fail
  - `source`가 단일 fallback에 95% 이상 쏠림: 원인 점검(키 누락/403/429)

### 실행 결과 (2026-03-10)

- `.env` 점검
  - `FINNHUB_API_KEY=__SET__`
  - `ALPHA_VANTAGE_API_KEY=__MISSING__`
  - `TWELVEDATA_API_KEY=__MISSING__`
  - `PRICE_FALLBACK_PROVIDERS=finnhub,twelvedata,alphavantage,stooq`
  - 판정: 충족 (`ALPHA_VANTAGE_API_KEY`, `TWELVEDATA_API_KEY`는 fallback용 선택 키로 미설정 허용)
- 실행 전 스냅샷
  - `total_rows=12550`
  - `max_price_date=2026-03-09`
  - source 분포: `yfinance=12550`
- 실행 로그
  - `Price sync complete: 50 rows upserted (0 inserted, 50 updated)`
  - `Price sync source breakdown (upserts): {'yfinance': 50}`
- 실행 후 검증
  - 최신일 source 분포: `yfinance=50`
  - 커버리지: `loaded=50 / total_active=7502 (0.67%)`
  - 최근 7일 source 비율: `yfinance=100.00%`
- 임계치 판정
  - 커버리지 `0.67%`로 `< 60%` 구간: `Fail`
  - fallback source 편중 판정은 fallback 미사용으로 N/A(yfinance only)

### 재실행 결과 (2026-03-10)

- 실행 로그
  - `Price sync candidates: 50 (filtered from 10412)`
  - `Price sync complete: 50 rows upserted (0 inserted, 50 updated)`
  - `Price sync source breakdown (upserts): {'yfinance': 50}`
- 실행 후 검증
  - `total_rows=12550`
  - `max_price_date=2026-03-09`
  - 최신일 source 분포: `yfinance=50`
  - 커버리지: `loaded=50 / total_active=7502 (0.67%)`
- 임계치 판정
  - 커버리지 `0.67%`로 `< 60%` 구간: `Fail` (변동 없음)

---

## 2) 바로 실행 가능한 SQL

> 아래 SQL은 Postgres 기준입니다.

### A. 실행 전/후 총 건수 비교

```sql
SELECT COUNT(*) AS total_rows
FROM price_daily;
```

### B. 최신 적재일 확인

```sql
SELECT MAX(price_date) AS max_price_date
FROM price_daily;
```

### C. 전체 source 분포

```sql
SELECT source, COUNT(*) AS rows
FROM price_daily
GROUP BY source
ORDER BY rows DESC;
```

### D. 최신 적재일 source 분포

```sql
WITH latest AS (
  SELECT MAX(price_date) AS d FROM price_daily
)
SELECT p.source, COUNT(*) AS rows
FROM price_daily p
JOIN latest l ON p.price_date = l.d
GROUP BY p.source
ORDER BY rows DESC;
```

### E. 최신 적재일 커버리지(활성 심볼 대비)

```sql
WITH latest AS (
  SELECT MAX(price_date) AS d FROM price_daily
),
active_symbols AS (
  SELECT COUNT(*) AS total_active
  FROM symbols
  WHERE is_active = true
    AND exchange IN ('Nasdaq', 'NYSE')
),
loaded_symbols AS (
  SELECT COUNT(DISTINCT p.symbol_id) AS loaded
  FROM price_daily p
  JOIN latest l ON p.price_date = l.d
)
SELECT
  a.total_active,
  l.loaded,
  ROUND((l.loaded::numeric / NULLIF(a.total_active, 0)) * 100, 2) AS coverage_pct
FROM active_symbols a
CROSS JOIN loaded_symbols l;
```

### F. 최근 N일 provider 편중 확인 (예: 7일)

```sql
SELECT
  source,
  COUNT(*) AS rows,
  ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER () * 100, 2) AS ratio_pct
FROM price_daily
WHERE price_date >= (CURRENT_DATE - INTERVAL '7 days')
GROUP BY source
ORDER BY rows DESC;
```

---

## 3) 테스트 케이스 템플릿 (pytest)

> 목적: fallback/파싱/업서트 요약 로직의 회귀 방지.

`packages/collectors/tests/test_price_sync_template.py` 예시 템플릿:

```python
import pytest


def test_finnhub_403_triggers_fallback(monkeypatch):
    """Finnhub 403이면 fallback provider가 호출되고 row가 반환되어야 한다."""
    # Arrange
    # - _finnhub_request -> FinnhubForbiddenError 발생
    # - _fallback_prices -> 샘플 row 반환
    # Act
    # - _fetch_symbol_prices(...) 실행
    # Assert
    # - 반환 rows 길이 > 0
    # - rows[0]['source'] == 기대 provider


def test_no_candle_triggers_fallback(monkeypatch):
    """Finnhub payload.s != 'ok'이면 fallback으로 내려가야 한다."""
    # Arrange: _finnhub_request returns {'s': 'no_data'}
    # Assert: fallback 결과 반환


def test_unknown_fallback_provider_is_skipped(caplog, monkeypatch):
    """미등록 provider가 설정되어도 warning 로그 후 다음 provider를 시도해야 한다."""
    # Arrange: PRICE_FALLBACK_PROVIDERS='unknown,finnhub'
    # Assert: warning 포함 + finnhub rows 반환


def test_provider_parser_filters_date_range():
    """provider parser는 start_date~until_date 범위만 남겨야 한다."""
    # Arrange: 범위 밖/안 데이터 혼합
    # Assert: 결과가 요청 범위로만 제한됨


def test_upsert_summary_counts_insert_vs_update(monkeypatch):
    """sync_daily_prices가 inserted/update 카운트를 정확히 집계하는지 검증."""
    # Arrange
    # - conn.execute(...).scalar_one() 이 True/False 섞어 반환되도록 stub
    # - 최소 2~3 row 시나리오 구성
    # Assert
    # - 최종 로그에 upserted/inserted/updated 숫자가 기대값과 일치


def test_source_breakdown_logging(monkeypatch, caplog):
    """source_totals 로그가 provider별 집계를 출력하는지 검증."""
    # Arrange: source가 섞인 rows 주입
    # Assert: 'Price sync source breakdown' 로그에 dict 반영
```

---

## 4) 권장 CI 최소 세트

- `python -m compileall packages/collectors/src`
- `pytest packages/collectors/tests -q`

(테스트가 아직 없다면 템플릿 파일부터 추가 후 점진적으로 구체화)
