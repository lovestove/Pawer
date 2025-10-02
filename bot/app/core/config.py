from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    BOT_TOKEN: str
    DATABASE_PATH: str
    LOG_LEVEL: str = "INFO"

    # Web server settings
    WEB_SERVER_HOST: str = "0.0.0.0"
    WEB_SERVER_PORT: int = 8000
    BASE_URL: str
    MINI_APP_URL: str


settings = Settings()