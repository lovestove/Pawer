from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_keyboard():
    """Главная клавиатура"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Моя статистика", callback_data="stats"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
        ],
        [
            InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help"),
            InlineKeyboardButton(text="💬 Обратная связь", callback_data="feedback")
        ]
    ])
    return keyboard


def get_settings_keyboard():
    """Клавиатура настроек"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔔 Уведомления", callback_data="toggle_notifications")
        ],
        [
            InlineKeyboardButton(text="🌍 Язык", callback_data="change_language")
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")
        ]
    ])
    return keyboard


def get_back_keyboard():
    """Простая кнопка назад"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_main")]
    ])
    return keyboard


def get_pet_keyboard():
    """Клавиатура для взаимодействия с питомцем"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🍖 Покормить", callback_data="pet_feed"),
            InlineKeyboardButton(text="💧 Напоить", callback_data="pet_water"),
            InlineKeyboardButton(text="🎾 Поиграть", callback_data="pet_play"),
        ],
        [
            InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_main")
        ]
    ])
    return keyboard