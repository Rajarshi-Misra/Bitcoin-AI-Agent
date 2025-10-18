from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    TOGETHER_API_KEY: str
    COIN_API: str
    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: str
    SECRET_KEY: str

settings = Settings()