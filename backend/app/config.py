from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ContextBridge"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://contextbridge:contextbridge@localhost:5432/contextbridge"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    openai_api_key: str = ""
    anthropic_api_key: str = ""


settings = Settings()
