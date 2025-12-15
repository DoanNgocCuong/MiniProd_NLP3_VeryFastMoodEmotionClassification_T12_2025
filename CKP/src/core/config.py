from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Groq configuration
    GROQ_API_KEY: str
    GROQ_MODEL: str = "openai/gpt-oss-20b"
    GROQ_TIMEOUT: float = 10.0

    # API configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 30031
    DEBUG: bool = False

    # Performance
    MAX_TOKENS_EMOTION: int = 10
    MAX_TOKENS_CELEBRATE: int = 5
    TEMPERATURE: float = 0.0
    TOP_P: float = 0.1

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

