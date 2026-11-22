from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "AIDoc"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str

    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "granite4.1:3b"

    CONFIDENCE_THRESHOLD: float = 0.80

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()