from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Настройки проекта
    PROJECT_NAME: str = "Todo List by Mitsuya"
    VERSION: str = "1.0.0"

    DATABASE_URL: str = "sqlite+aiosqlite:///todo.sqlite3"

    ALLOWED_ORIGINS: list[str] = ["http://127.0.0.1:8000", "http://localhost:8000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()