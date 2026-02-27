"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All settings with sensible defaults for local development."""

    # Database
    database_url: str = "postgresql+asyncpg://glicmack:glicmack_dev@localhost:5432/glicmack"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Ollama
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # Rate limiting
    max_generations_per_day: int = 10
    max_prompt_length: int = 500

    # Environment
    env: str = "development"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
