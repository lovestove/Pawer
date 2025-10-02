# 💰 Руководство по монетизации Pawer

## Текущая система монетизации

### 🪙 Внутриигровая валюта (Монеты)

**Способы получения:**
- Уход за питомцем: +2 монеты за действие
- Повышение уровня: +50 монет
- Ежедневная награда: 50-200 монет (зависит от streak)
- Выполнение квестов (можно добавить)

**Использование:**
- Покупка еды в магазине
- Покупка предметов
- Ускорители (можно добавить)

### 🏪 Магазин

**Категории товаров:**

1. **Еда (10-150 монет)**
   - Хлеб: 10 монет (+10 сытость)
   - Яблоко: 20 монет (+15 сытость, +5 здоровье)
   - Мясо: 35 монет (+25 сытость)
   - Пицца: 50 монет (+30 сытость, +10 счастье)
   - Торт: 60 монет (+20 счастье)
   - Золотое яблоко: 150 монет (все статы +30)

2. **Предметы (80-200 монет)**
   - Мяч: 80 монет
   - Игрушка: 100 монет (+15 счастье)
   - Кровать: 200 монет (улучшает сон)
   - Зелье энергии: 120 монет (+50 энергия)

## 📈 Расширенная монетизация

### Вариант 1: Telegram Stars (рекомендуется)

**Преимущества:**
- Встроенная система оплаты Telegram
- Нет комиссий платёжных систем
- Безопасно и удобно
- Доступно глобально

**Реализация:**

```python
# bot/app/handlers/payments.py
from aiogram import Router
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from aiogram.filters import Command

router = Router()

PRICES = {
    'coins_100': LabeledPrice(label='100 монет', amount=99),  # 0.99$
    'coins_500': LabeledPrice(label='500 монет', amount=399),  # 3.99$
    'coins_1000': LabeledPrice(label='1000 монет', amount=699),  # 6.99$
    'premium_month': LabeledPrice(label='Premium на месяц', amount=499),  # 4.99$
}

@router.message(Command("buy"))
async def cmd_buy(message: Message):
    """Покупка монет"""
    await message.answer_invoice(
        title="Набор монет 🪙",
        description="100 монет для покупок в магазине",
        payload="coins_100",
        provider_token="",  # Пусто для Stars
        currency="XTR",  # Telegram Stars
        prices=[PRICES['coins_100']],
    )

@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout: PreCheckoutQuery):
    """Подтверждение оплаты"""
    await pre_checkout.answer(ok=True)

@router.message(F.successful_payment)
async def process_successful_payment(message: Message, db: Database):
    """Обработка успешной оплаты"""
    user_id = message.from_user.id
    payload = message.successful_payment.invoice_payload
    
    if payload == "coins_100":
        await db.add_coins(user_id, 100, "Покупка 100 монет")
        await message.answer("✅ 100 монет зачислено! 🪙")
```

**Пакеты монет:**
- 100 монет = 99 Stars (≈$0.99)
- 500 монет = 399 Stars (≈$3.99) - скидка 20%
- 1000 монет = 699 Stars (≈$6.99) - скидка 30%
- 2500 монет = 1499 Stars (≈$14.99) - скидка 40%

### Вариант 2: Premium подписка

**Преимущества Premium:**
- ❌ Нет рекламы (если добавите)
- 🎁 Ежедневный бонус x2
- ⚡ XP x1.5
- 🎨 Эксклюзивные питомцы
- 💎 Эксклюзивные предметы
- 🏆 Premium badge в рейтинге
- 🐾 3 слота для питомцев (вместо 1)

**Цены:**
- Месяц: 499 Stars (≈$4.99)
- 3 месяца: 1299 Stars (≈$12.99) - скидка 13%
- Год: 3999 Stars (≈$39.99) - скидка 33%

**Реализация Premium:**

```python
# bot/app/core/database.py
async def set_premium(self, user_id: int, days: int):
    """Активация premium"""
    expires_at = datetime.now() + timedelta(days=days)
    async with aiosqlite.connect(self.db_path) as db:
        await db.execute("""
            UPDATE users 
            SET premium_until = ?
            WHERE user_id = ?
        """, (expires_at.isoformat(), user_id))
        await db.commit()

async def is_premium(self, user_id: int) -> bool:
    """Проверка premium статуса"""
    async with aiosqlite.connect(self.db_path) as db:
        cursor = await db.execute("""
            SELECT premium_until FROM users WHERE user_id = ?
        """, (user_id,))
        row = await cursor.fetchone()
        
        if row and row[0]:
            expires = datetime.fromisoformat(row[0])
            return expires > datetime.now()
        return False
```

### Вариант 3: Реклама

**Rewarded Video Ads:**
- Пользователь смотрит рекламу → получает награду
- 10 монет за просмотр
- 1 бесплатный премиум предмет
- +50 XP

**Платформы:**
- AdMob (для веба через iframe)
- Telegram Ads (когда появится для Mini Apps)

**Реализация:**

```javascript
// В mini_app/index.html
async watchAd() {
    // Интеграция с AdMob
    if (window.adBreak) {
        await window.adBreak({
            type: 'reward',
            name: 'watch-ad-reward',
            beforeReward: () => {
                this.showToast('📺', 'Смотрим рекламу...');
            },
            adComplete: async () => {
                // Начисляем награду
                await fetch(`${this.apiUrl}/ad/reward`, {
                    method: 'POST',
                    body: JSON.stringify({ user_id: this.userId })
                });
                this.pet.coins += 10;
                this.showToast('🎁', 'Получено +10 монет за просмотр!');
            }
        });
    }
}
```

### Вариант 4: Реферальная программа

**Механика:**
- Пригласивший: +50 монет за друга
- Приглашённый: +30 монет при старте
- Бонус за активных друзей: +10 монет/день если друг заходит

**Реализация:**

```python
# bot/app/handlers/referral.py
@router.message(Command("ref"))
async def cmd_ref(message: Message):
    """Реферальная ссылка"""
    user_id = message.from_user.id
    bot_username = (await message.bot.me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    await message.answer(
        f"🎁 <b>Пригласи друзей!</b>\n\n"
        f"Твоя ссылка:\n{ref_link}\n\n"
        f"💰 За каждого друга: +50 монет\n"
        f"🎁 Твой друг получит: +30 монет",
        parse_mode="HTML"
    )

@router.message(CommandStart(deep_link=True))
async def cmd_start_ref(message: Message, db: Database):
    """Обработка реферала"""
    args = message.text.split()[1] if len(message.text.split()) > 1 else None
    
    if args and args.startswith('ref_'):
        referrer_id = int(args.split('_')[1])
        new_user_id = message.from_user.id
        
        if referrer_id != new_user_id:
            # Проверяем, новый ли пользователь
            pet = await db.get_pet(new_user_id)
            if not pet:
                # Начисляем бонусы
                await db.add_coins(referrer_id, 50, "Реферал")
                await db.add_coins(new_user_id, 30, "Бонус за приглашение")
                
                await message.answer(
                    f"🎁 Получено +30 монет от друга!\n"
                    f"Начни своё приключение!"
                )
```

## 💎 VIP предметы и питомцы

### Эксклюзивные питомцы (Premium)

**Легендарные питомцы (только Premium):**
- 🦄 Единорог
- 🐉 Дракон
- 🦚 Феникс
- 🌟 Звёздный кот

**Реализация:**

```javascript
// Проверка premium перед выбором яйца
async selectEgg(eggId) {
    const egg = this.eggs.find(e => e.id === eggId);
    
    if (egg.premium && !this.user.isPremium) {
        this.showModal(
            '💎',
            'Premium питомец',
            'Этот питомец доступен только с Premium подпиской',
            () => this.showPremiumOffer()
        );
        return;
    }
    
    this.selectedEgg = eggId;
}
```

### Лутбоксы (Gacha)

**Честная система:**
- Прозрачные шансы
- Гарантированный эпик каждые 10 открытий
- Нет дубликатов легендарок

**Типы ящиков:**
- Обычный: 50 монет
  - 70% обычный предмет
  - 25% редкий
  - 5% эпический
  
- Редкий: 150 монет
  - 50% редкий
  - 40% эпический
  - 10% легендарный

- Легендарный: 500 монет
  - 60% эпический
  - 35% легендарный
  - 5% мифический

## 📊 Балансировка экономики

### Источники монет (за день)

**F2P игрок:**
- Уход за питомцем: 20-30 монет (10-15 действий)
- Ежедневная награда: 50-100 монет
- Квесты: 30-50 монет
- **Итого: 100-180 монет/день**

**Premium игрок:**
- Уход: 40-60 монет (x2)
- Ежедневная награда: 100-200 монет (x2)
- Квесты: 60-100 монет (x2)
- Premium бонус: 50 монет
- **Итого: 250-410 монет/день**

### Траты монет

**Обязательные:**
- Еда: 50-100 монет/день

**Опциональные:**
- Предметы: 80-200 монет
- Лутбоксы: 50-500 монет
- Косметика: 100-500 монет

### Конверсия Free → Paid

**Оптимальные точки продажи:**

1. **День 3** - Первое предложение premium
   - 50% скидка на первый месяц
   - "Попробуй premium 3 дня бесплатно"

2. **Уровень 10** - Достижение
   - Специальный набор монет со скидкой
   - "Отпразднуй успех!"

3. **Нехватка монет** - В магазине
   - "Не хватает 20 монет? Купи набор!"
   - Показываем выгодные пакеты

4. **Легендарный питомец** - При попытке взять
   - "Получи premium и получи эксклюзивного питомца!"

## 💡 Стратегии удержания

### Daily Streak

**Награды по дням:**
- День 1: 50 монет
- День 2: 60 монет
- День 3: 70 монет
- День 7: 100 монет + редкий предмет
- День 14: 150 монет + эпический предмет
- День 30: 300 монет + легендарный питомец

**Защита от потери streak:**
- Premium: автоматическая защита (1 пропуск = ок)
- Предмет "Заморозка streak": 100 монет

### Battle Pass (сезонный)

**Длительность:** 30 дней

**Free track:**
- 10 уровней
- Обычные награды
- Бесплатная косметика

**Premium track:** 299 Stars
- 30 уровней
- Эксклюзивный питомец
- Много монет и предметов
- Уникальная косметика

### Ивенты

**Еженедельные:**
- Выходные x2 XP
- "Счастливый час": x2 монеты за действия

**Месячные:**
- Сезонные ивенты (Хэллоуин, Новый год)
- Специальные питомцы
- Ограниченная косметика

## 📈 Метрики успеха

### KPI для отслеживания

**Монетизация:**
- ARPU (средний доход с пользователя)
- ARPPU (средний доход с платящего)
- Conversion rate (% платящих)
- LTV (lifetime value)

**Вовлечённость:**
- DAU/MAU ratio
- Retention D1, D7, D30
- Session length
- Actions per session

**Целевые показатели (первый год):**
- Conversion: 3-5%
- ARPU: $0.50-1.00
- ARPPU: $15-20
- D1 Retention: 40%+
- D7 Retention: 20%+
- D30 Retention: 10%+

## 🎯 Рекомендации

### Что делать:
✅ Прозрачные цены
✅ Честные шансы в gacha
✅ Щедрые награды для F2P
✅ Premium даёт преимущества, но не Pay-to-Win
✅ Частые ивенты и обновления

### Чего избегать:
❌ Агрессивные pop-up
❌ Pay-to-Win механики
❌ Обманчивые предложения
❌ Слишком дорогие цены
❌ Mandatory ads (только rewarded)

## 🚀 План запуска монетизации

**Неделя 1-2:**
- Запуск с базовыми покупками монет
- A/B тесты цен

**Неделя 3-4:**
- Добавление premium подписки
- Реферальная программа

**Месяц 2:**
- Первый Battle Pass
- Лутбоксы

**Месяц 3+:**
- Оптимизация на основе данных
- Новые монетизационные фичи
- Ивенты и сезоны

---

**Помните:** Главное - баланс между монетизацией и user experience! 💚