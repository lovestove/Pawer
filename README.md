# Pawer Telegram Bot

Это простой Telegram-бот, созданный с использованием библиотеки `aiogram`.

## Установка

1.  Клонируйте репозиторий:
    ```bash
    git clone <URL репозитория>
    cd <название папки>
    ```

2.  Создайте и активируйте виртуальное окружение (рекомендуется):
    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Windows: venv\Scripts\activate
    ```

3.  Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

## Настройка

1.  Получите токен для вашего бота у [@BotFather](https://t.me/BotFather) в Telegram.

2.  Создайте в корне проекта файл `.env` и добавьте в него ваш токен:
    ```
    TELEGRAM_BOT_TOKEN="1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ```
    Либо установите переменную окружения `TELEGRAM_BOT_TOKEN` любым другим удобным для вас способом.

## Запуск

Для запуска бота выполните команду:
```bash
python bot.py
```