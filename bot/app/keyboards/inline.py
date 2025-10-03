from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ..core.config import GameConfig, settings

def get_main_menu(has_pet: bool) -> InlineKeyboardMarkup:
    """Генерация главного меню в зависимости от наличия питомца"""
    buttons = [
        [InlineKeyboardButton(text="🐾 Открыть приложение 🐾", web_app={"url": settings.MINI_APP_URL})]
    ]
    if has_pet:
        buttons.extend([
            [InlineKeyboardButton(text="📊 Статистика", callback_data="profile"), InlineKeyboardButton(text="🏆 Рейтинг", callback_data="leaderboard")],
            [InlineKeyboardButton(text="🎁 Ежедневный бонус", callback_data="daily_reward"), InlineKeyboardButton(text="👥 Друзья", callback_data="friends")]
        ])
    else:
        buttons.append([InlineKeyboardButton(text="✨ Создать питомца", callback_data="create_pet")])
    
    buttons.append([InlineKeyboardButton(text="💰 Магазин", callback_data="shop"), InlineKeyboardButton(text="❓ Помощь", callback_data="help")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_pet_type_keyboard(owned_eggs: list) -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора типа питомца из доступных яиц"""
    buttons = []
    for egg_type in owned_eggs:
        if pet_info := GameConfig.PET_TYPES.get(egg_type):
            buttons.append([InlineKeyboardButton(text=f"{pet_info['emoji']} {pet_info['name']}", callback_data=f"pettype_{egg_type}")])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

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

def get_coin_packages_keyboard():
    """Создает клавиатуру с пакетами монет"""
    buttons = []
    for i, pkg in enumerate(GameConfig.COIN_PACKAGES):
        bonus_text = f" (+{pkg['bonus']}% 🔥)" if pkg['bonus'] > 0 else ""
        button_text = f"{pkg['coins']} 🪙 за {pkg['price_rub']}₽{bonus_text}"
        buttons.append([InlineKeyboardButton(text=button_text, callback_data=f"coinpkg_{i}")])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_shop")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_gem_packages_keyboard():
    """Создает клавиатуру с пакетами гемов"""
    buttons = []
    for i, pkg in enumerate(GameConfig.GEM_PACKAGES):
        button_text = f"{pkg['gems']} 💎 за {pkg['price_rub']}₽"
        buttons.append([InlineKeyboardButton(text=button_text, callback_data=f"gempkg_{i}")])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_shop")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_payment_method_keyboard(package_type: str, package_index: int):
    """Создает клавиатуру для выбора метода оплаты"""
    buttons = [
        [InlineKeyboardButton(text="⭐ Оплатить Stars", callback_data=f"pay_stars_{package_type}_{package_index}")],
        [InlineKeyboardButton(text="💳 Оплатить ЮMoney", callback_data=f"pay_yoomoney_{package_type}_{package_index}")],
        [InlineKeyboardButton(text="🏦 Оплатить СБП", callback_data=f"pay_sbp_{package_type}_{package_index}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"buy_{package_type}s")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
