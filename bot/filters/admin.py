from ..config_reader import admin_list
from aiogram.filters import Filter
from aiogram.types import Message

class IsAdminFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in admin_list