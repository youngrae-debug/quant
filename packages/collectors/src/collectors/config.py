from pydantic_settings import BaseSettings, SettingsConfigDict


class CollectorSettings(BaseSettings):
    database_url: str = 'postgresql+psycopg://quant:quant@localhost:5432/quant'
    sec_user_agent: str = 'quant-research/0.1 (ops@example.com)'
    finnhub_api_key: str = ''
    finnhub_base_url: str = 'https://finnhub.io/api/v1'
    alpha_vantage_api_key: str = ''
    twelvedata_api_key: str = ''
    price_fallback_providers: str = 'finnhub,twelvedata,alphavantage,stooq'
    sec_base_url: str = 'https://data.sec.gov'
    symbol_default_lookback_days: int = 365
    request_timeout_seconds: int = 30
    rate_limit_sleep_seconds: float = 1.5

    model_config = SettingsConfigDict(env_file='.env', env_prefix='', extra='ignore')


settings = CollectorSettings()
