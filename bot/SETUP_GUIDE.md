# 🚀 Полное руководство по запуску Pawer

## Шаг 1: Создание бота в Telegram

### 1.1 Создайте бота через BotFather

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot`
3. Придумайте имя: например `Pawer Pet`
4. Придумайте username: например `YourPawerBot` (должен заканчиваться на `bot`)
5. **Сохраните токен!** Он выглядит так: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### 1.2 Настройте бота

```
/setdescription - Заботься о своём цифровом питомце! 🐾

/setabouttext - Pawer - это твой персональный цифровой питомец в Telegram. Корми, играй и заботься о нём каждый день!

/setuserpic - Загрузите иконку (рекомендуем эмодзи 🐾)

/setcommands - Установите команды:
start - Начать работу с ботом
app - Открыть приложение
stats - Статистика питомца
shop - Магазин предметов
daily - Ежедневная награда
leaderboard - Таблица лидеров
help - Помощь по использованию
```

### 1.3 Настройте Mini App

**Важно!** Для локальной разработки используйте ngrok.

#### Установка ngrok

1. Скачайте: https://ngrok.com/download
2. Распакуйте и добавьте в PATH
3. Запустите:
```bash
ngrok http 8000
```

4. Скопируйте HTTPS URL (например: `https://abc123.ngrok-free.app`)

#### Настройка в BotFather

```
/mybots -> Выберите вашего бота -> Bot Settings -> Menu Button

Введите:
- Button text: 🐾 Мой питомец
- URL: https://your-ngrok-url.ngrok-free.app
```

## Шаг 2: Локальный запуск

### 2.1 Подготовка окружения

```bash
# Клонируйте или создайте проект
cd Pawer/bot

# Создайте виртуальное окружение
python -m venv venv

# Активируйте
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Установите зависимости
pip install -r requirements.txt
```

### 2.2 Настройка .env

Создайте `bot/.env`:

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
DATABASE_PATH=pawer.db
BASE_URL=https://abc123.ngrok-free.app
MINI_APP_URL=https://abc123.ngrok-free.app
WEB_PORT=8000
LOG_LEVEL=INFO
```

**Важно:** Замените URL на ваш ngrok URL!

### 2.3 Скопируйте Mini App

Убедитесь что файл `mini_app/index.html` на месте.

### 2.4 Запустите бота

```bash
cd bot
python run.py
```

Вы должны увидеть:
```
INFO - База данных инициализирована
INFO - Бот запущен: @YourPawerBot
INFO - Mini App URL: https://abc123.ngrok-free.app
INFO - Веб-сервер запущен на порту 8000
```

### 2.5 Тестирование

1. Откройте вашего бота в Telegram
2. Отправьте `/start`
3. Нажмите кнопку "🐾 Открыть приложение"
4. Приложение должно открыться!

## Шаг 3: Продакшн деплой

### 3.1 Подготовка сервера

Требования:
- Ubuntu 20.04+ или другой Linux
- Python 3.11+
- Nginx
- Домен с SSL сертификатом

#### 3.1.1 Обновите систему

```bash
sudo apt update && sudo apt upgrade -y
```

#### 3.1.2 Установите зависимости

```bash
sudo apt install python3.11 python3.11-venv python3-pip nginx certbot python3-certbot-nginx git -y
```

### 3.2 Настройка домена и SSL

#### 3.2.1 Получите SSL сертификат

```bash
sudo certbot --nginx -d your-domain.com
```

Следуйте инструкциям certbot.

#### 3.2.2 Настройте Nginx

Создайте `/etc/nginx/sites-available/pawer`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Активируйте:
```bash
sudo ln -s /etc/nginx/sites-available/pawer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3.3 Деплой приложения

#### 3.3.1 Загрузите код

```bash
cd /opt
sudo git clone <your-repo-url> pawer
sudo chown -R $USER:$USER /opt/pawer
cd pawer/bot
```

#### 3.3.2 Настройте окружение

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3.3.3 Создайте .env

```bash
nano .env
```

```env
BOT_TOKEN=your_real_token
DATABASE_PATH=/opt/pawer/data/pawer.db
BASE_URL=https://your-domain.com
MINI_APP_URL=https://your-domain.com
WEB_PORT=8000
LOG_LEVEL=INFO
```

Создайте директорию для БД:
```bash
mkdir -p /opt/pawer/data
```

### 3.4 Systemd Service

Создайте `/etc/systemd/system/pawer.service`:

```ini
[Unit]
Description=Pawer Telegram Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/opt/pawer/bot
Environment="PATH=/opt/pawer/bot/venv/bin"
ExecStart=/opt/pawer/bot/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Замените `your-username` на ваш пользователь Linux.

Запустите:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pawer
sudo systemctl start pawer
sudo systemctl status pawer
```

### 3.5 Обновите настройки бота

Вернитесь в BotFather:
```
/mybots -> Ваш бот -> Bot Settings -> Menu Button
URL: https://your-domain.com
```

### 3.6 Тестирование продакшна

1. Откройте бота
2. `/start`
3. Нажмите кнопку Menu
4. Всё должно работать!

## Шаг 4: Мониторинг

### 4.1 Просмотр логов

```bash
# Реальное время
sudo journalctl -u pawer -f

# Последние 100 строк
sudo journalctl -u pawer -n 100

# Ошибки
sudo journalctl -u pawer -p err
```

### 4.2 Перезапуск

```bash
sudo systemctl restart pawer
```

### 4.3 Остановка

```bash
sudo systemctl stop pawer
```

### 4.4 Резервное копирование БД

```bash
# Создайте cron job
crontab -e

# Добавьте (бэкап каждый день в 3:00)
0 3 * * * cp /opt/pawer/data/pawer.db /opt/pawer/backups/pawer_$(date +\%Y\%m\%d).db
```

## Шаг 5: Обновление

### 5.1 Загрузите новый код

```bash
cd /opt/pawer
git pull
```

### 5.2 Обновите зависимости

```bash
cd bot
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### 5.3 Перезапустите

```bash
sudo systemctl restart pawer
```

## 🐛 Решение проблем

### Бот не запускается

**Проверьте логи:**
```bash
sudo journalctl -u pawer -n 50
```

**Проверьте .env:**
```bash
cat /opt/pawer/bot/.env
```

**Проверьте права:**
```bash
ls -la /opt/pawer/data/
```

### Mini App не открывается

**Проверьте Nginx:**
```bash
sudo nginx -t
sudo systemctl status nginx
```

**Проверьте порт:**
```bash
sudo netstat -tulpn | grep 8000
```

**Проверьте SSL:**
```bash
sudo certbot certificates
```

### База данных повреждена

**Восстановите из бэкапа:**
```bash
cp /opt/pawer/backups/pawer_YYYYMMDD.db /opt/pawer/data/pawer.db
sudo systemctl restart pawer
```

### Высокая нагрузка

**Проверьте количество пользователей:**
```bash
sqlite3 /opt/pawer/data/pawer.db "SELECT COUNT(*) FROM users;"
```

**Оптимизируйте БД:**
```bash
sqlite3 /opt/pawer/data/pawer.db "VACUUM;"
```

## 📊 Аналитика

### Статистика в БД

```bash
sqlite3 /opt/pawer/data/pawer.db

# Количество пользователей
SELECT COUNT(*) FROM users;

# Активные пользователи (последние 24ч)
SELECT COUNT(*) FROM users 
WHERE last_active > datetime('now', '-1 day');

# Топ-10 игроков
SELECT u.first_name, p.level, p.coins 
FROM pets p 
JOIN users u ON p.user_id = u.user_id 
ORDER BY p.level DESC, p.xp DESC 
LIMIT 10;

# Общая статистика по монетам
SELECT SUM(coins) as total_coins FROM pets;

# Транзакции
SELECT type, SUM(amount), COUNT(*) 
FROM transactions 
GROUP BY type;
```

## 🔐 Безопасность

### Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Автообновление SSL

Certbot уже настроил auto-renewal, но проверьте:
```bash
sudo certbot renew --dry-run
```

### Бэкапы

Настройте автоматические бэкапы на внешний сервер/облако.

## ✅ Чеклист запуска

- [ ] Бот создан в BotFather
- [ ] Token сохранён
- [ ] Домен куплен и настроен (для прода)
- [ ] SSL сертификат получен
- [ ] Nginx настроен
- [ ] Код загружен на сервер
- [ ] .env настроен
- [ ] Зависимости установлены
- [ ] Systemd service создан и запущен
- [ ] Menu button настроена в BotFather
- [ ] Бот протестирован
- [ ] Логи проверены
- [ ] Бэкапы настроены
- [ ] Мониторинг работает

## 🎉 Готово!

Ваш Pawer бот готов к работе! Удачи! 🐾