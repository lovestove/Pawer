from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Union, List, Any

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

    # Payment provider tokens
    STARS_ENABLED: bool = True
    YOOMONEY_TOKEN: Union[str, None] = None
    YOOMONEY_WALLET: Union[str, None] = None

    # Game settings
    ADMIN_IDS: List[int] = []
    REFERRAL_REWARD_COINS: int = 100
    REFERRAL_REWARD_GEMS: int = 5

    @field_validator('ADMIN_IDS', mode='before')
    @classmethod
    def split_admin_ids(cls, v: Any) -> List[int]:
        if isinstance(v, (int, float)):
            return [int(v)]
        if isinstance(v, str):
            if not v.strip():
                return []
            return [int(i.strip()) for i in v.split(',') if i.strip()]
        return v


settings = Settings()


class GameConfig:
    """Конфигурация игровых пакетов и параметров"""
    COIN_PACKAGES = [
        {"coins": 1000, "price_rub": 100, "price_stars": 50, "bonus": 0},
        {"coins": 5000, "price_rub": 450, "price_stars": 225, "bonus": 10},
        {"coins": 10000, "price_rub": 800, "price_stars": 400, "bonus": 20},
    ]
    GEM_PACKAGES = [
        {"gems": 10, "price_rub": 100, "price_stars": 50},
        {"gems": 50, "price_rub": 450, "price_stars": 225},
        {"gems": 100, "price_rub": 800, "price_stars": 400},
    ]

    PET_TYPES = {
        'basic': {'name': 'Обычный котик', 'emoji': '🐱', 'egg': 'basic'},
        'rare': {'name': 'Редкий котик', 'emoji': '🦄', 'egg': 'rare'},
        'legendary': {'name': 'Легендарный', 'emoji': '🐉', 'egg': 'legendary'}
    }

    @staticmethod
    def exp_for_level(level: int) -> int:
        """Рассчитывает опыт для следующего уровня"""
        return int(100 * (level ** 1.5))
