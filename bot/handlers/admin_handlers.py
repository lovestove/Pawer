from aiogram.types import Message
import aiogram.filters as filters
from ..filters.admin import IsAdminFilter
from aiogram import Router, F
from ..keyboards.inline import inline_main_menu, inline_main_menu_admin

router = Router()

router.message.filter(IsAdminFilter())

@router.message(filters.Command(commands=['admin']))
async def admin_panel(message: Message):
    await message.answer('Привет, мой дорогой админ!', reply_markup=inline_main_menu_admin())
