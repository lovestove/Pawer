import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiohttp import web

from app.core.config import settings
from app.core.database import db
from app.handlers import start, shop, eggs, payment, friends
from app.web.server import create_app

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    await db.init()
    logger.info("База данных инициализирована")

    bot_info = await bot.get_me()
    logger.info(f"Бот запущен: @{bot_info.username}")


async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    logger.info("Бот остановлен")


async def start_bot():
    """Запуск бота"""
    bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(shop.router)
    dp.include_router(eggs.router)
    dp.include_router(payment.router)
    dp.include_router(friends.router)

    # Регистрация событий
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Запуск polling
    await dp.start_polling(bot)


async def start_web():
    """Запуск веб-сервера"""
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()

    logger.info(f"Веб-сервер запущен на {settings.BASE_URL}")


async def main():
    """Главная функция"""
    # Запуск веб-сервера и бота параллельно
    await asyncio.gather(
        start_web(),
        start_bot()
    )


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Остановка приложения...")