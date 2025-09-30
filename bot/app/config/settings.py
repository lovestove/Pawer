"""
Модуль для управления настройками приложения.

Этот модуль использует Pydantic's BaseSettings для управления конфигурацией
приложения. Настройки загружаются из переменных окружения.

Attributes:
    bot_token (str): Токен для Telegram Bot API.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Класс для хранения настроек приложения.

    Атрибуты загружаются из переменных окружения. Для локальной разработки
    можно использовать файл .env в директории /bot.
    """
    bot_token: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')


# Создаем экземпляр настроек, который будет использоваться в приложении
settings = Settings()