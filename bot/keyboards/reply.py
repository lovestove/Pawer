from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def reply_main() -> ReplyKeyboardMarkup:

    kb = ReplyKeyboardBuilder()

    kb.button(text='❤️приветик')
    kb.button(text='🥹дада?')

    kb.adjust(3)

    return kb.as_markup(resize_keyboard=True)
