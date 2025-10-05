from aiogram import Router, F
import aiogram.types as types
from aiogram.types import Message, CallbackQuery
import aiogram.filters as filters
from ..keyboards.reply import reply_main
from ..keyboards.inline import inline_start_bot, inline_main_menu

router = Router()

@router.message(filters.CommandStart())
async def cmd_start(message: Message):

    await message.answer(f"""
Привет! Добро пожаловать в Pawer!
Это не просто бот, а целая вселенная,
которая позволит тебе растить своего любимого 
питомца, ухаживать за ним в одиночку или со
своими друзьями. Ну что {message.from_user.first_name}
ты готов(а)??
    """,
                         reply_markup=inline_start_bot())

@router.message(F.data == 'main_menu')
async def main_menu(callback: CallbackQuery):
    await callback.answer('''
Добро пожаловать в главное меню!
    ''', reply_markup=inline_main_menu())
