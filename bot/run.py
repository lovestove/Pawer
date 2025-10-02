import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.core import settings, Database
from app.handlers import setup_handlers
from app.middlewares import user_middleware


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

    # Передача экземпляра базы данных в хендлеры
    dp["db"] = db

    # Настройка middleware
    dp.message.middleware(user_middleware)

    # Настройка хендлеров
    router = setup_handlers()
    dp.include_router(router)

    # Удаление старых обновлений и запуск polling
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot started!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")