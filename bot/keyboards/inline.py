from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo


def inline_start_bot() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(text='Начать!', callback_data='main_menu')

    kb.adjust(1)

    return kb.as_markup()


def inline_main_menu_admin() -> InlineKeyboardMarkup:

    kb = InlineKeyboardBuilder(markup=inline_main_menu().markup)

    kb.button(text='Админ панель', callback_data='admin_panel')

    kb.adjust(1)

    return kb.as_markup()


def inline_main_menu() -> InlineKeyboardMarkup:

    kb = InlineKeyboardBuilder()

    kb.adjust(2)

    kb.button(text='Привеееет!^^', url='https://lovestove.github.io/Pawer/')

    return kb.as_markup()