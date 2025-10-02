# 📁 Структура проекта Pawer

## Полная структура файлов

```
Pawer/
│
├── bot/                                    # Основная директория бота
│   │
│   ├── app/                                # Приложение
│   │   │
│   │   ├── core/                           # Ядро системы
│   │   │   ├── __init__.py
│   │   │   ├── config.py                   # Конфигурация (Settings)
│   │   │   └── database.py                 # Работа с БД (Database class)
│   │   │
│   │   ├── handlers/                       # Обработчики команд
│   │   │   ├── __init__.py
│   │   │   ├── main.py                     # Основные команды (/start, /help, etc)
│   │   │   └── payments.py                 # Платежи (опционально)
│   │   │
│   │   ├── keyboards/                      # Клавиатуры
│   │   │   ├── __init__.py
│   │   │   ├── webapp.py                   # Web App кнопки
│   │   │   └── inline.py                   # Inline клавиатуры
│   │   │
│   │   ├── middlewares/                    # Middleware (опционально)
│   │   │   ├── __init__.py
│   │   │   └── db.py                       # DB middleware
│   │   │
│   │   └── web/                            # Web сервер для Mini App
│   │       ├── __init__.py
│   │       └── api.py                      # REST API endpoints
│   │
│   ├── mini_app/                           # Telegram Mini App
│   │   └── index.html                      # Единственный HTML файл (все в одном)
│   │
│   ├── .env                                # Переменные окружения (не коммитить!)
│   ├── .env.example                        # Пример .env
│   ├── .gitignore                          # Git ignore
│   ├── Dockerfile                          # Docker образ
│   ├── requirements.txt                    # Python зависимости
│   └── run.py                              # Точка входа (главный файл)
│
├── data/                                   # Данные (создаётся автоматически)
│   └── pawer.db                            # SQLite база данных
│
├── backups/                                # Бэкапы БД (создать вручную)
│   └── pawer_YYYYMMDD.db
│
├── logs/                                   # Логи (опционально)
│   └── bot.log
│
├── docker-compose.yml                      # Docker Compose конфигурация
├── README.md                               # Основная документация
├── SETUP_GUIDE.md                          # Руководство по установке
├── MONETIZATION.md                         # Руководство по монетизации
└── PROJECT_STRUCTURE.md                    # Этот файл
```

## 📄 Описание ключевых файлов

### Bot Core

#### `bot/run.py`
**Назначение:** Точка входа, запуск бота и веб-сервера
**Содержит:**
- Инициализацию бота и диспетчера
- Запуск веб-сервера (aiohttp)
- Регистрацию handlers и middleware
- Startup/shutdown логику

#### `bot/app/core/config.py`
**Назначение:** Конфигурация приложения
**Содержит:**
- Settings class (pydantic)
- Все переменные окружения
- Игровые константы (XP, монеты, скорость decay)

#### `bot/app/core/database.py`
**Назначение:** Все операции с БД
**Основные методы:**
- `init_db()` - создание таблиц
- `create_pet()` - создание питомца
- `get_pet()` - получение питомца
- `update_pet()` - обновление данных
- `add_coins()`, `spend_coins()` - работа с монетами
- `check_daily_reward()`, `claim_daily_reward()` - ежедневные награды
- `get_leaderboard()` - рейтинг
- `add_to_inventory()`, `get_inventory()` - инвентарь

### Handlers

#### `bot/app/handlers/main.py`
**Назначение:** Основные команды бота
**Команды:**
- `/start` - приветствие
- `/app` - открыть Mini App
- `/stats` - статистика питомца
- `/shop` - магазин
- `/daily` - ежедневная награда
- `/leaderboard` - рейтинг
- `/help` - помощь

### Web API

#### `bot/app/web/api.py`
**Назначение:** REST API для Mini App
**Endpoints:**
- `GET /api/pet/get` - получить питомца
- `POST /api/pet/create` - создать питомца
- `POST /api/pet/update` - обновить питомца
- `POST /api/shop/buy` - купить предмет
- `GET /api/inventory/get` - получить инвентарь
- `GET /api/leaderboard` - таблица лидеров

### Mini App

#### `bot/mini_app/index.html`
**Назначение:** Весь Mini App в одном файле
**Содержит:**
- HTML разметку
- CSS стили (inline)
- JavaScript логику
- Telegram WebApp API интеграцию

**Основные компоненты:**
- Welcome screen (ввод имени)
- Egg selection (выбор яйца)
- Main screen (главный экран с питомцем)
- Shop screen (магазин)
- Navigation (нижнее меню)

## 🗄️ Схема базы данных

### Таблица `users`
```sql
user_id INTEGER PRIMARY KEY      -- Telegram user ID
username TEXT                    -- Telegram username
first_name TEXT                  -- Имя пользователя
created_at TIMESTAMP             -- Дата регистрации
last_active TIMESTAMP            -- Последняя активность
premium_until TIMESTAMP          -- До когда premium (NULL = нет)
```

### Таблица `pets`
```sql
id INTEGER PRIMARY KEY           -- ID питомца
user_id INTEGER UNIQUE           -- Владелец (FK -> users)
name TEXT NOT NULL               -- Имя питомца
emoji TEXT NOT NULL              -- Эмодзи питомца
egg_type INTEGER                 -- Тип яйца (1-4)
level INTEGER DEFAULT 1          -- Уровень
xp INTEGER DEFAULT 0             -- Опыт
coins INTEGER DEFAULT 100        -- Монеты
stats TEXT NOT NULL              -- JSON со статами (health, happiness, energy, hunger)
created_at TIMESTAMP             -- Дата создания
last_updated TIMESTAMP           -- Последнее обновление
```

### Таблица `daily_rewards`
```sql
user_id INTEGER PRIMARY KEY      -- Пользователь (FK)
last_claim TIMESTAMP             -- Когда последний раз получил
streak INTEGER DEFAULT 1         -- Серия дней подряд
```

### Таблица `inventory`
```sql
id INTEGER PRIMARY KEY           -- ID записи
user_id INTEGER                  -- Владелец (FK)
item_id TEXT NOT NULL            -- ID предмета
quantity INTEGER DEFAULT 1       -- Количество
```

### Таблица `transactions`
```sql
id INTEGER PRIMARY KEY           -- ID транзакции
user_id INTEGER                  -- Пользователь (FK)
type TEXT NOT NULL               -- Тип (earn, spend, daily_reward)
amount INTEGER NOT NULL          -- Сумма (+ или -)
description TEXT                 -- Описание
created_at TIMESTAMP             -- Дата
```

## 🔄 Поток данных

### Создание питомца

```
Пользователь          Mini App           API                Database
    |                    |                |                    |
    |--ввод имени------->|                |                    |
    |                    |                |                    |
    |--выбор яйца------->|                |                    |
    |                    |                |                    |
    |--тап "Получить"--->|                |                    |
    |                    |                |                    |
    |                    |--POST /api/pet/create------------>  |
    |                    |                |                    |
    |                    |                |--INSERT pets------>|
    |                    |                |                    |
    |                    |<-----pet data--|<---row-------------|
    |                    |                |                    |
    |<--показ питомца----|                |                    |
```

### Действие с питомцем (например, кормление)

```
Пользователь          Mini App           API                Database
    |                    |                |                    |
    |--нажал "Кормить"-->|                |                    |
    |                    |                |                    |
    |                    |--локальное обновление статов------>|
    |                    |                |                    |
    |<--анимация---------|                |                    |
    |                    |                |                    |
    |                    |--POST /api/pet/update------------>  |
    |                    |                |                    |
    |                    |                |--UPDATE pets------>|
    |                    |                |                    |
    |                    |<-----success---|                    |
```

### Покупка в магазине

```
Пользователь          Mini App           API                Database
    |                    |                |                    |
    |--выбрал предмет--->|                |                    |
    |                    |                |                    |
    |--подтвердил------->|                |                    |
    |                    |                |                    |
    |                    |--POST /api/shop/buy-------------->  |
    |                    |                |                    |
    |                    |                |--проверка монет--->|
    |                    |                |                    |
    |                    |                |--списание--------->|
    |                    |                |                    |
    |                    |                |--добавить в inventory->|
    |                    |                |                    |
    |                    |<-----success---|                    |
    |                    |                |                    |
    |--обновление UI-----|                |                    |
```

## 🔌 API спецификация

### Все endpoints возвращают JSON

**Формат успешного ответа:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Формат ошибки:**
```json
{
  "success": false,
  "error": "Error message"
}
```

### Детальные примеры

#### GET /api/pet/get
**Query params:**
- `user_id` (required): Telegram user ID

**Response:**
```json
{
  "success": true,
  "pet": {
    "id": 1,
    "user_id": 123456789,
    "name": "Пушистик",
    "emoji": "🐱",
    "level": 5,
    "xp": 350,
    "coins": 250,
    "stats": {
      "health": 85,
      "happiness": 90,
      "energy": 70,
      "hunger": 60
    }
  }
}
```

#### POST /api/pet/create
**Body:**
```json
{
  "user_id": 123456789,
  "name": "Пушистик",
  "emoji": "🐱",
  "egg_type": 1
}
```

**Response:** то же что и GET /api/pet/get

#### POST /api/pet/update
**Body:**
```json
{
  "user_id": 123456789,
  "pet": {
    "name": "Пушистик",
    "level": 5,
    "xp": 350,
    "coins": 250,
    "stats": { ... }
  }
}
```

**Response:**
```json
{
  "success": true
}
```

## 🎮 Игровая логика

### Снижение статов

**Частота:** Каждые 60 секунд (настраивается)

**Скорость:**
- Hunger: -1.0 в минуту
- Energy: -0.5 в минуту
- Happiness: -0.3 в минуту (если другие статы низкие)
- Health: не снижается автоматически

**Реализация:** JavaScript setInterval в Mini App

### Получение XP

**За действия:**
- Покормить: +5 XP
- Играть: +10 XP
- Помыть: +5 XP
- Спать: +8 XP

**Формула уровня:**
- Требуется: `уровень * 100` XP
- Пример: для уровня 5 → 500 XP

**При повышении уровня:**
- +50 монет
- Уведомление пользователю

### Ежедневные награды

**Базовая:** 50 монет

**Бонус за streak:**
- День 1: 50
- День 2: 60 (+10)
- День 3: 70 (+10)
- ...
- Макс: 200 монет

**Защита streak:**
- Допустимый пропуск: 48 часов
- Если > 48ч: streak сбрасывается

## 🚀 Расширения

### Будущие фичи (готовая структура)

#### PvP битвы
```
bot/app/handlers/battles.py
bot/app/web/battles_api.py
Новая таблица: battles
```

#### Система друзей
```
bot/app/handlers/friends.py
Новые таблицы: friends, friend_requests
```

#### Достижения
```
bot/app/core/achievements.py
Новая таблица: achievements
```

#### Квесты
```
bot/app/handlers/quests.py
Новые таблицы: quests, user_quests
```

## 📦 Зависимости

### Python (requirements.txt)
- `aiogram==3.15.0` - Telegram Bot API
- `aiohttp==3.11.10` - Async HTTP (веб-сервер)
- `aiosqlite==0.20.0` - Async SQLite
- `pydantic==2.10.3` - Валидация данных
- `pydantic-settings==2.6.1` - Настройки из .env
- `python-dotenv==1.0.1` - Загрузка .env

### JavaScript (