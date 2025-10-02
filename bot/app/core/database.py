import logging
from datetime import datetime
import aiosqlite

logger = logging.getLogger(__name__)


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

            # Таблица для питомцев
            await db.execute('''
                CREATE TABLE IF NOT EXISTS pets (
                    pet_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    name TEXT NOT NULL,
                    hunger INTEGER DEFAULT 100,
                    thirst INTEGER DEFAULT 100,
                    happiness INTEGER DEFAULT 100,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            await db.commit()
            logger.info("База данных инициализирована")

    async def create_pet(self, user_id: int, name: str):
        """Создание нового питомца"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO pets (user_id, name, last_updated) VALUES (?, ?, ?)
            ''', (user_id, name, datetime.now()))
            await db.commit()
            logger.info(f"Создан новый питомец '{name}' для пользователя {user_id}")

    async def get_pet(self, user_id: int):
        """Получение данных о питомце пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM pets WHERE user_id = ?', (user_id,)) as cursor:
                pet_data = await cursor.fetchone()
                return dict(pet_data) if pet_data else None

    async def update_pet_stats(self, user_id: int, hunger: int, thirst: int, happiness: int):
        """Обновление статов питомца"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE pets
                SET hunger = ?, thirst = ?, happiness = ?, last_updated = ?
                WHERE user_id = ?
            ''', (hunger, thirst, happiness, datetime.now(), user_id))
            await db.commit()

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