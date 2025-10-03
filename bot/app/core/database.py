import aiosqlite
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from .config import settings, GameConfig


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    coins INTEGER DEFAULT 100,
                    gems INTEGER DEFAULT 5,
                    streak_days INTEGER DEFAULT 0,
                    last_login TEXT,
                    referrer_id INTEGER,
                    referral_count INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Таблица питомцев
            await db.execute("""
                CREATE TABLE IF NOT EXISTS pets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    pet_type TEXT DEFAULT 'basic',
                    level INTEGER DEFAULT 1,
                    exp INTEGER DEFAULT 0,
                    hunger INTEGER DEFAULT 100,
                    happiness INTEGER DEFAULT 100,
                    energy INTEGER DEFAULT 100,
                    hygiene INTEGER DEFAULT 100,
                    last_update TEXT DEFAULT CURRENT_TIMESTAMP,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)

            # Таблица инвентаря
            await db.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    item_id TEXT NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    UNIQUE(user_id, item_id)
                )
            """)

            # Таблица кастомизации
            await db.execute("""
                CREATE TABLE IF NOT EXISTS customization (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pet_id INTEGER,
                    item_id TEXT NOT NULL,
                    slot TEXT,
                    is_equipped INTEGER DEFAULT 0,
                    FOREIGN KEY (pet_id) REFERENCES pets(id)
                )
            """)

            # Таблица купленных яиц
            await db.execute("""
                CREATE TABLE IF NOT EXISTS owned_eggs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    pet_type TEXT NOT NULL,
                    purchased_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    UNIQUE(user_id, pet_type)
                )
            """)

            # Таблица транзакций
            await db.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    type TEXT NOT NULL,
                    amount INTEGER,
                    currency TEXT,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)

            await db.commit()

    # === ПОЛЬЗОВАТЕЛИ ===
    async def create_user(self, user_id: int, username: str, referrer_id: Optional[int] = None) -> bool:
        """Создание нового пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO users (user_id, username, referrer_id) VALUES (?, ?, ?)",
                    (user_id, username, referrer_id)
                )
                await db.commit()

                # Награда рефереру
                if referrer_id:
                    await self.add_coins(referrer_id, settings.REFERRAL_REWARD_COINS)
                    await self.add_gems(referrer_id, settings.REFERRAL_REWARD_GEMS)
                    await db.execute(
                        "UPDATE users SET referral_count = referral_count + 1 WHERE user_id = ?",
                        (referrer_id,)
                    )
                    await db.commit()

                return True
        except aiosqlite.IntegrityError:
            return False

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def update_streak(self, user_id: int) -> Tuple[int, int]:
        """Обновление серии дней"""
        async with aiosqlite.connect(self.db_path) as db:
            user = await self.get_user(user_id)
            if not user:
                return 0, 0

            last_login = user.get('last_login')
            today = datetime.now().date()

            if last_login:
                last_date = datetime.fromisoformat(last_login).date()
                diff = (today - last_date).days

                if diff == 0:
                    # Уже заходил сегодня
                    return user['streak_days'], 0
                elif diff == 1:
                    # Продолжение серии
                    new_streak = user['streak_days'] + 1
                else:
                    # Серия прервана
                    new_streak = 1
            else:
                new_streak = 1

            # Награда за вход
            coins_reward = settings.REFERRAL_REWARD_COINS
            gems_reward = 0

            # Бонусы за серию
            if new_streak % 7 == 0:
                gems_reward = 5
            elif new_streak % 3 == 0:
                coins_reward += 50

            await db.execute(
                "UPDATE users SET streak_days = ?, last_login = ? WHERE user_id = ?",
                (new_streak, datetime.now().isoformat(), user_id)
            )
            await db.commit()

            await self.add_coins(user_id, coins_reward)
            if gems_reward > 0:
                await self.add_gems(user_id, gems_reward)

            return new_streak, coins_reward + gems_reward * 10

    async def add_coins(self, user_id: int, amount: int):
        """Добавить монеты"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET coins = coins + ? WHERE user_id = ?",
                (amount, user_id)
            )
            await db.commit()

    async def remove_coins(self, user_id: int, amount: int) -> bool:
        """Удалить монеты"""
        async with aiosqlite.connect(self.db_path) as db:
            user = await self.get_user(user_id)
            if user and user['coins'] >= amount:
                await db.execute(
                    "UPDATE users SET coins = coins - ? WHERE user_id = ?",
                    (amount, user_id)
                )
                await db.commit()
                return True
            return False

    async def add_gems(self, user_id: int, amount: int):
        """Добавить гемы"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET gems = gems + ? WHERE user_id = ?",
                (amount, user_id)
            )
            await db.commit()

    async def remove_gems(self, user_id: int, amount: int) -> bool:
        """Удалить гемы"""
        async with aiosqlite.connect(self.db_path) as db:
            user = await self.get_user(user_id)
            if user and user['gems'] >= amount:
                await db.execute(
                    "UPDATE users SET gems = gems - ? WHERE user_id = ?",
                    (amount, user_id)
                )
                await db.commit()
                return True
            return False

    # === ПИТОМЦЫ ===
    async def create_pet(self, user_id: int, name: str, pet_type: str = 'basic') -> Optional[int]:
        """Создание питомца"""
        async with aiosqlite.connect(self.db_path) as db:
            # Деактивируем других питомцев
            await db.execute(
                "UPDATE pets SET is_active = 0 WHERE user_id = ?",
                (user_id,)
            )

            cursor = await db.execute(
                """INSERT INTO pets (user_id, name, pet_type) 
                   VALUES (?, ?, ?)""",
                (user_id, name, pet_type)
            )
            await db.commit()
            return cursor.lastrowid

    async def get_active_pet(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение активного питомца"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                    "SELECT * FROM pets WHERE user_id = ? AND is_active = 1",
                    (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    pet = dict(row)
                    # Обновляем параметры
                    await self._update_pet_stats(pet)
                    return pet
                return None

    async def _update_pet_stats(self, pet: Dict[str, Any]):
        """Обновление параметров питомца с учетом времени"""
        last_update = datetime.fromisoformat(pet['last_update'])
        now = datetime.now()
        hours_passed = (now - last_update).total_seconds() / 3600

        if hours_passed > 0:
            # Уменьшаем параметры
            pet['hunger'] = max(0, pet['hunger'] - int(hours_passed * GameConfig.HUNGER_DECREASE_RATE))
            pet['happiness'] = max(0, pet['happiness'] - int(hours_passed * GameConfig.HAPPINESS_DECREASE_RATE))
            pet['energy'] = max(0, pet['energy'] - int(hours_passed * GameConfig.ENERGY_DECREASE_RATE))
            pet['hygiene'] = max(0, pet['hygiene'] - int(hours_passed * GameConfig.HYGIENE_DECREASE_RATE))

            # Сохраняем
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """UPDATE pets SET hunger = ?, happiness = ?, energy = ?, 
                       hygiene = ?, last_update = ? WHERE id = ?""",
                    (pet['hunger'], pet['happiness'], pet['energy'],
                     pet['hygiene'], now.isoformat(), pet['id'])
                )
                await db.commit()

    async def update_pet_stat(self, pet_id: int, stat: str, value: int):
        """Обновление параметра питомца"""
        async with aiosqlite.connect(self.db_path) as db:
            value = max(0, min(100, value))
            await db.execute(
                f"UPDATE pets SET {stat} = ?, last_update = ? WHERE id = ?",
                (value, datetime.now().isoformat(), pet_id)
            )
            await db.commit()

    async def add_exp(self, pet_id: int, amount: int) -> Optional[int]:
        """Добавление опыта и проверка повышения уровня"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM pets WHERE id = ?", (pet_id,)) as cursor:
                pet = await cursor.fetchone()
                if not pet:
                    return None

                new_exp = pet['exp'] + amount
                new_level = pet['level']

                # Проверка повышения уровня
                while new_exp >= GameConfig.exp_for_level(new_level):
                    new_exp -= GameConfig.exp_for_level(new_level)
                    new_level += 1

                    # Награда за уровень
                    await self.add_coins(pet['user_id'], GameConfig.LEVEL_UP_COINS)
                    await self.add_gems(pet['user_id'], GameConfig.LEVEL_UP_GEMS)

                await db.execute(
                    "UPDATE pets SET exp = ?, level = ? WHERE id = ?",
                    (new_exp, new_level, pet_id)
                )
                await db.commit()

                return new_level if new_level > pet['level'] else None

    # === ИНВЕНТАРЬ ===
    async def add_item(self, user_id: int, item_id: str, quantity: int = 1):
        """Добавление предмета в инвентарь"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO inventory (user_id, item_id, quantity) 
                   VALUES (?, ?, ?)
                   ON CONFLICT(user_id, item_id) 
                   DO UPDATE SET quantity = quantity + ?""",
                (user_id, item_id, quantity, quantity)
            )
            await db.commit()

    async def remove_item(self, user_id: int, item_id: str, quantity: int = 1) -> bool:
        """Удаление предмета из инвентаря"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                    "SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?",
                    (user_id, item_id)
            ) as cursor:
                row = await cursor.fetchone()
                if not row or row['quantity'] < quantity:
                    return False

                new_quantity = row['quantity'] - quantity
                if new_quantity > 0:
                    await db.execute(
                        "UPDATE inventory SET quantity = ? WHERE user_id = ? AND item_id = ?",
                        (new_quantity, user_id, item_id)
                    )
                else:
                    await db.execute(
                        "DELETE FROM inventory WHERE user_id = ? AND item_id = ?",
                        (user_id, item_id)
                    )
                await db.commit()
                return True

    async def get_inventory(self, user_id: int) -> List[Dict[str, Any]]:
        """Получение инвентаря"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                    "SELECT * FROM inventory WHERE user_id = ?",
                    (user_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_item_quantity(self, user_id: int, item_id: str) -> int:
        """Получение количества предмета"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                    "SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?",
                    (user_id, item_id)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    # === КАСТОМИЗАЦИЯ ===
    async def add_customization(self, pet_id: int, item_id: str, slot: Optional[str] = None):
        """Добавление предмета кастомизации"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO customization (pet_id, item_id, slot) VALUES (?, ?, ?)",
                (pet_id, item_id, slot)
            )
            await db.commit()

    async def equip_item(self, pet_id: int, item_id: str, slot: str):
        """Надеть предмет"""
        async with aiosqlite.connect(self.db_path) as db:
            # Снимаем другие предметы в этом слоте
            await db.execute(
                "UPDATE customization SET is_equipped = 0 WHERE pet_id = ? AND slot = ?",
                (pet_id, slot)
            )
            # Надеваем новый
            await db.execute(
                "UPDATE customization SET is_equipped = 1 WHERE pet_id = ? AND item_id = ?",
                (pet_id, item_id)
            )
            await db.commit()

    async def unequip_item(self, pet_id: int, item_id: str):
        """Снять предмет"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE customization SET is_equipped = 0 WHERE pet_id = ? AND item_id = ?",
                (pet_id, item_id)
            )
            await db.commit()

    async def get_equipped_items(self, pet_id: int) -> List[Dict[str, Any]]:
        """Получение надетых предметов"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                    "SELECT * FROM customization WHERE pet_id = ? AND is_equipped = 1",
                    (pet_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    # === ЯЙЦА ===
    async def add_owned_egg(self, user_id: int, pet_type: str) -> bool:
        """Добавить купленное яйцо"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO owned_eggs (user_id, pet_type) VALUES (?, ?)",
                    (user_id, pet_type)
                )
                await db.commit()
                return True
        except aiosqlite.IntegrityError:
            return False

    async def get_owned_eggs(self, user_id: int) -> List[str]:
        """Получить купленные яйца"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                    "SELECT pet_type FROM owned_eggs WHERE user_id = ?",
                    (user_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    async def has_egg(self, user_id: int, pet_type: str) -> bool:
        """Проверить наличие яйца"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                    "SELECT 1 FROM owned_eggs WHERE user_id = ? AND pet_type = ?",
                    (user_id, pet_type)
            ) as cursor:
                return await cursor.fetchone() is not None

    # === ТРАНЗАКЦИИ ===
    async def add_transaction(self, user_id: int, type: str, amount: int,
                              currency: str, description: str):
        """Добавить транзакцию"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO transactions (user_id, type, amount, currency, description) 
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, type, amount, currency, description)
            )
            await db.commit()


# Глобальная база данных
db = Database(settings.DATABASE_PATH)
