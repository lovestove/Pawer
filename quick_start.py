import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties

# Исправленные импорты для запуска из корня проекта
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_reader import config
from handlers import user_handlers, admin_handlers
from database.engine import init_db

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""

    # Инициализируем базу данных
    logger.info('🔧 Инициализация базы данных...')
    init_db()

    # Создаем бота
    logger.info('🤖 Запуск бота...')
    bot = Bot(
        token=config.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    # Подключаем роутеры (админы первые, чтобы их фильтр сработал раньше)
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)

    # Удаляем старые обновления
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info('✅ Бот запущен и готов к работе!')
    logger.info('Для остановки нажми Ctrl+C')

    # Запускаем polling
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info('🛑 Бот остановлен пользователем')
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('👋 До свидания!')