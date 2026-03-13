from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


COLLECTORS_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = COLLECTORS_DIR / '.env'


class CollectorSettings(BaseSettings):
    database_url: str = 'postgresql+psycopg://quant:quant@localhost:5432/quant'
    sec_user_agent: str = 'quant-research/0.1 (ops@example.com)'
    finnhub_api_key: str = 'd6noe59r01qse5qmfkbgd6noe59r01qse5qmfkc0'
    finnhub_base_url: str = 'https://finnhub.io/api/v1'
    alpha_vantage_api_key: str = 'Q8RU6FANTNKDPJRE'
    twelvedata_api_key: str = 'f5ca75f1e8c34ac49d4b77ebc479df1c'
    price_fallback_providers: str = 'alphavantage,polygon,twelvedata,yfinance,stooq'
    sec_base_url: str = 'https://data.sec.gov'
    symbol_default_lookback_days: int = 365
    request_timeout_seconds: int = 30
    rate_limit_sleep_seconds: float = 1.5

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_prefix='', extra='ignore')


settings = CollectorSettings()
