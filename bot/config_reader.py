from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    BOT_TOKEN: SecretStr
    DATABASE_PATH: str
    LOG_LEVEL: str
    ADMIN_IDS: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

config = Settings()

admin_list = [int(admin) for admin in config.ADMIN_IDS.split(',')]