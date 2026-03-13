from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


APP_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = APP_DIR / '.env'


class Settings(BaseSettings):
    app_name: str = 'quant-api'
    app_env: str = 'development'
    database_url: str = 'postgresql+psycopg://quant:quant@localhost:5432/quant'
    cors_origins: Annotated[list[str], NoDecode] = ['http://localhost:3000']

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(',') if origin.strip()]
        return value

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_prefix='', extra='ignore')


settings = Settings()