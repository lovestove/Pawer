import logging
import asyncio
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import aiosqlite
from dotenv import load_dotenv

load_dotenv()

# ============= КОНФИГУРАЦИЯ =============
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_PATH = os.getenv("DATABASE_PATH")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ============= ЛОГИРОВАНИЕ =============
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============= FSM STATES (для диалогов) =============
class UserStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_feedback = State()


# ============= БАЗА ДАННЫХ =============
class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init_db(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица пользователей
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_premium INTEGER DEFAULT 0,
                    balance INTEGER DEFAULT 0
                )
            ''')

            # Таблица статистики
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_stats (
                    user_id INTEGER PRIMARY KEY,
                    messages_sent INTEGER DEFAULT 0,
                    commands_used INTEGER DEFAULT 0,
                    last_activity TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            # Таблица для хранения настроек
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY,
                    notifications INTEGER DEFAULT 1,
                    language TEXT DEFAULT 'ru',
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            await db.commit()
            logger.info("База данных инициализирована")

    async def add_user(self, user_id: int, username: str = None,
                       first_name: str = None, last_name: str = None):
        """Добавление нового пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute('''
                    INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name))

                await db.execute('''
                    INSERT OR IGNORE INTO user_stats (user_id, last_activity)
                    VALUES (?, ?)
                ''', (user_id, datetime.now()))

                await db.execute('''
                    INSERT OR IGNORE INTO user_settings (user_id)
                    VALUES (?)
                ''', (user_id,))

                await db.commit()
            except Exception as e:
                logger.error(f"Ошибка добавления пользователя: {e}")

    async def update_stats(self, user_id: int, stat_type: str):
        """Обновление статистики пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            if stat_type == "message":
                await db.execute('''
                    UPDATE user_stats 
                    SET messages_sent = messages_sent + 1, last_activity = ?
                    WHERE user_id = ?
                ''', (datetime.now(), user_id))
            elif stat_type == "command":
                await db.execute('''
                    UPDATE user_stats 
                    SET commands_used = commands_used + 1, last_activity = ?
                    WHERE user_id = ?
                ''', (datetime.now(), user_id))
            await db.commit()

    async def get_user_stats(self, user_id: int):
        """Получение статистики пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT * FROM user_stats WHERE user_id = ?
            ''', (user_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def get_all_users(self):
        """Получение всех пользователей (для рассылки)"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT user_id FROM users') as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]


# ============= КЛАВИАТУРЫ =============
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


# ============= ИНИЦИАЛИЗАЦИЯ БОТА =============
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
db = Database(DATABASE_PATH)


# ============= MIDDLEWARE (для автоматического добавления юзеров) =============
@dp.message.middleware()
async def user_middleware(handler, event: Message, data: dict):
    """Middleware для регистрации пользователей"""
    user = event.from_user
    await db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    await db.update_stats(user.id, "message")
    return await handler(event, data)


# ============= КОМАНДЫ =============
@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Команда /start"""
    await db.update_stats(message.from_user.id, "command")

    welcome_text = f"""
🎉 <b>Привет, {message.from_user.first_name}!</b>

Добро пожаловать в бота! Вот что я умею:

📊 Статистика - смотри свою активность
⚙️ Настройки - персонализируй бота
💬 Обратная связь - свяжись с нами
ℹ️ Помощь - список всех команд

Выбери действие ниже:
"""

    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Команда /help"""
    await db.update_stats(message.from_user.id, "command")

    help_text = """
📚 <b>Список команд:</b>

/start - Главное меню
/help - Справка по командам
/stats - Твоя статистика
/settings - Настройки
/feedback - Обратная связь

💡 <b>Совет:</b> Используй кнопки для удобной навигации!
"""

    await message.answer(
        help_text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )


@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    """Команда /stats"""
    await db.update_stats(message.from_user.id, "command")

    stats = await db.get_user_stats(message.from_user.id)

    if stats:
        stats_text = f"""
📊 <b>Твоя статистика:</b>

💬 Сообщений отправлено: {stats['messages_sent']}
⚡ Команд использовано: {stats['commands_used']}
🕐 Последняя активность: {stats['last_activity'][:16]}

Продолжай в том же духе! 🚀
"""
    else:
        stats_text = "📊 Статистика пока недоступна"

    await message.answer(
        stats_text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )


@dp.message(Command("settings"))
async def cmd_settings(message: Message):
    """Команда /settings"""
    await db.update_stats(message.from_user.id, "command")

    settings_text = """
⚙️ <b>Настройки бота</b>

Здесь ты можешь настроить бота под себя.
Выбери параметр:
"""

    await message.answer(
        settings_text,
        reply_markup=get_settings_keyboard(),
        parse_mode="HTML"
    )


# ============= CALLBACK HANDLERS (кнопки) =============
@dp.callback_query(F.data == "stats")
async def callback_stats(callback: CallbackQuery):
    """Показать статистику через кнопку"""
    stats = await db.get_user_stats(callback.from_user.id)

    if stats:
        stats_text = f"""
📊 <b>Твоя статистика:</b>

💬 Сообщений отправлено: {stats['messages_sent']}
⚡ Команд использовано: {stats['commands_used']}
🕐 Последняя активность: {stats['last_activity'][:16]}

Продолжай в том же духе! 🚀
"""
    else:
        stats_text = "📊 Статистика пока недоступна"

    await callback.message.edit_text(
        stats_text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.callback_query(F.data == "settings")
async def callback_settings(callback: CallbackQuery):
    """Открыть настройки"""
    settings_text = """
⚙️ <b>Настройки бота</b>

Здесь ты можешь настроить бота под себя.
Выбери параметр:
"""

    await callback.message.edit_text(
        settings_text,
        reply_markup=get_settings_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery):
    """Показать помощь"""
    help_text = """
📚 <b>Список команд:</b>

/start - Главное меню
/help - Справка по командам
/stats - Твоя статистика
/settings - Настройки
/feedback - Обратная связь

💡 <b>Совет:</b> Используй кнопки для удобной навигации!
"""

    await callback.message.edit_text(
        help_text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.callback_query(F.data == "feedback")
async def callback_feedback(callback: CallbackQuery, state: FSMContext):
    """Начать процесс обратной связи"""
    await callback.message.edit_text(
        "💬 <b>Обратная связь</b>\n\nНапиши свой вопрос или предложение:",
        parse_mode="HTML"
    )
    await state.set_state(UserStates.waiting_for_feedback)
    await callback.answer()


@dp.callback_query(F.data == "back_to_main")
async def callback_back(callback: CallbackQuery):
    """Вернуться в главное меню"""
    welcome_text = f"""
🎉 <b>Главное меню</b>

Выбери действие:
"""

    await callback.message.edit_text(
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.callback_query(F.data == "toggle_notifications")
async def callback_toggle_notifications(callback: CallbackQuery):
    """Переключение уведомлений"""
    await callback.answer("🔔 Уведомления обновлены!", show_alert=True)


@dp.callback_query(F.data == "change_language")
async def callback_change_language(callback: CallbackQuery):
    """Смена языка"""
    await callback.answer("🌍 Выбор языка (в разработке)", show_alert=True)


# ============= FSM HANDLERS (диалоги) =============
@dp.message(StateFilter(UserStates.waiting_for_feedback))
async def process_feedback(message: Message, state: FSMContext):
    """Обработка обратной связи"""
    # Здесь можно отправить админу или сохранить в БД
    feedback_text = message.text

    # Уведомляем пользователя
    await message.answer(
        "✅ <b>Спасибо за обратную связь!</b>\n\nМы обязательно рассмотрим твоё сообщение.",
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )

    # Логируем для админа
    logger.info(f"Feedback from {message.from_user.id}: {feedback_text}")

    # Сбрасываем состояние
    await state.clear()


# ============= ОБРАБОТКА ОБЫЧНЫХ СООБЩЕНИЙ =============
@dp.message(F.text)
async def handle_text(message: Message):
    """Обработка текстовых сообщений"""
    # Простой эхо-бот для примера
    await message.answer(
        f"Ты написал: {message.text}\n\nИспользуй /start для главного меню",
        reply_markup=get_back_keyboard()
    )


@dp.message(F.photo)
async def handle_photo(message: Message):
    """Обработка фото"""
    await message.answer(
        "📸 Получил фото! В будущем здесь будет обработка изображений.",
        reply_markup=get_back_keyboard()
    )


@dp.message(F.document)
async def handle_document(message: Message):
    """Обработка документов"""
    await message.answer(
        "📄 Получил документ! Пока не обрабатываю файлы.",
        reply_markup=get_back_keyboard()
    )


# ============= ЗАПУСК БОТА =============
async def main():
    """Главная функция запуска"""
    # Инициализируем БД
    await db.init_db()

    # Удаляем старые обновления
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("🚀 Бот запущен!")

    # Запускаем polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен")
