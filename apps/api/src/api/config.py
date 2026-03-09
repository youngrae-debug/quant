from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = 'quant-api'
    app_env: str = 'development'
    database_url: str = 'postgresql+psycopg://quant:quant@db:5432/quant'
    cors_origins: list[str] = ['http://localhost:3000']

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(',') if origin.strip()]
        return value

    model_config = SettingsConfigDict(env_file='.env', env_prefix='')


settings = Settings()
