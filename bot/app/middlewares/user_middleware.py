from aiogram.types import Message
from app.core import Database


async def user_middleware(handler, event: Message, data: dict):
    """Middleware для регистрации пользователей"""
    user = event.from_user
    db: Database = data["db"]

    await db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    await db.update_stats(user.id, "message")
    return await handler(event, data)