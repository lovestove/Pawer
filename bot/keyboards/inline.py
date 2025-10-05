from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


def inline_start_bot() -> InlineKeyboardMarkup:
    """Стартовая клавиатура"""
    kb = InlineKeyboardBuilder()

    kb.button(text='🎨 Создать питомца', callback_data='create_pet')
    kb.adjust(1)

    return kb.as_markup()


def inline_create_pet() -> InlineKeyboardMarkup:
    """Клавиатура выбора вида питомца"""
    kb = InlineKeyboardBuilder()

    kb.button(text='🐱 Киберкот', callback_data='species_cyber_cat')
    kb.button(text='🐉 Дракончик', callback_data='species_dragon')
    kb.button(text='☁️ Облачко', callback_data='species_cloud')
    kb.button(text='🤖 Робопёс', callback_data='species_robo_dog')

    kb.adjust(2)

    return kb.as_markup()


def inline_main_menu() -> InlineKeyboardMarkup:
    """Главное меню с Mini App и быстрыми действиями"""
    kb = InlineKeyboardBuilder()

    # Главная кнопка - открыть Mini App
    kb.button(
        text='🎮 Открыть приложение',
        web_app=WebAppInfo(url='https://lovestove.github.io/Pawer/')
    )

    # Быстрые действия
    kb.button(text='🍞 Быстро покормить', callback_data='quick_feed')
    kb.button(text='🎯 Быстро поиграть', callback_data='quick_play')

    # Статистика
    kb.button(text='📊 Статистика', callback_data='pet_stats')

    kb.adjust(1, 2, 1)

    return kb.as_markup()


def inline_main_menu_admin() -> InlineKeyboardMarkup:
    """Админское меню"""
    kb = InlineKeyboardBuilder()

    # Добавляем обычное меню
    kb.button(
        text='🎮 Открыть приложение',
        web_app=WebAppInfo(url='https://lovestove.github.io/Pawer/')
    )

    kb.button(text='🍞 Быстро покормить', callback_data='quick_feed')
    kb.button(text='🎯 Быстро поиграть', callback_data='quick_play')
    kb.button(text='📊 Статистика', callback_data='pet_stats')

    # Админские кнопки
    kb.button(text='⚙️ Админ панель', callback_data='admin_panel')

    kb.adjust(1, 2, 1, 1)

    return kb.as_markup()