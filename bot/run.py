import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

from app.core import settings, Database
from app.handlers import setup_handlers
from app.middlewares import user_middleware
from app.web.app import create_web_app


async def main():
    """Главная функция запуска"""
    # Конфигурация логирования
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    # Инициализация базы данных
    db = Database(settings.DATABASE_PATH)
    await db.init_db()

    # Инициализация бота и диспетчера
    bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Передача экземпляра базы данных в хендлеры и middleware
    dp["db"] = db

    # Настройка middleware
    dp.message.middleware(user_middleware)

    # Настройка хендлеров
    router = setup_handlers()
    dp.include_router(router)

    # Создание и запуск веб-приложения
    web_app = create_web_app(db=db)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, settings.WEB_SERVER_HOST, settings.WEB_SERVER_PORT)

    logger.info("Starting bot and web server...")

    # Удаление старых обновлений
    await bot.delete_webhook(drop_pending_updates=True)

    # Запуск обоих приложений
    try:
        await asyncio.gather(
            dp.start_polling(bot),
            site.start(),
        )
    finally:
        await runner.cleanup()
        await bot.session.close()
        logger.info("Bot and web server stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Application stopped.")