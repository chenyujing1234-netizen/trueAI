from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = Field(
        default="mysql+pymysql://chenyujing:Centerm1%40@114.55.254.123:3306/trueai"
    )
    JWT_SECRET: str = Field(default="trueai_dev_secret")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRES_MINUTES: int = Field(default=60 * 24 * 7)

    LLM_PROVIDER: str = Field(default="qwen")
    DASHSCOPE_API_KEY: str = Field(default="")
    QWEN_MODEL: str = Field(default="qwen-plus")

    CORS_ORIGINS: str = Field(default="http://localhost:3000")

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
