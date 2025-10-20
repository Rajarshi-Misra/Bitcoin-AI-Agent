from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    TOGETHER_API_KEY: str
    COIN_API: str
    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SECRET_KEY: str
    REDIS_URL: str

    class Config:
        env_file = ".env"

settings = Settings()