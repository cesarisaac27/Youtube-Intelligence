from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):

    #API KEYS
    YOUTUBE_API_KEY: str

    # AI service (optional, for channel analysis)
    YOUTUBE_AI_TOKEN: Optional[str] = None
    API_AI_URL: Optional[str] = None
    API_AI_MODEL: Optional[str] = None
    VITE_API_URL: Optional[str] = None

    #Database rest
    PROJECT_URL: str
    PROJECT_KEY: str

    #DB Credentials
    USER: str
    PASSWORD: str
    HOST: str
    PORT: int
    DBNAME: str
    
    ENV: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """
    Cacheamos settings para que se cree una sola vez
    """
    return Settings()


settings = get_settings()
