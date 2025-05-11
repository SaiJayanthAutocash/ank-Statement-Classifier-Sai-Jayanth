from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Bank Statement Classifier"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite:///./bank.db"
    SQLALCHEMY_DATABASE_URL: str = DATABASE_URL

    # JWT settings (Bonus: Authentication)
    SECRET_KEY: str = "Xjb9-2BNOFQj7oA3zbYYT9Q9rbcKid1Uv5fZJvvpEng"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
