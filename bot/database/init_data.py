"""
Начальные данные для базы данных
Запусти этот файл один раз после создания БД чтобы добавить стартовые предметы
"""
from sqlalchemy.orm import Session
from .models import Item
from .engine import get_db


def add_starter_items():
    """Добавить стартовые предметы в БД"""
    db = get_db()

    # Проверяем, есть ли уже предметы
    existing = db.query(Item).first()
    if existing:
        print('⚠️ Предметы уже добавлены в БД!')
        return

    print('📦 Добавление стартовых предметов...')

    # === ЕДА ===
    foods = [
        # Бесплатная еда
        Item(
            name='Хлеб',
            description='Простой хлеб. Лучше чем ничего!',
            item_type='food',
            rarity='common',
            health_effect=10,
            happiness_effect=5,
            coin_price=0,
            icon_emoji='🍞'
        ),
        Item(
            name='Вода',
            description='Чистая вода. Освежает!',
            item_type='food',
            rarity='common',
            health_effect=5,
            energy_effect=10,
            coin_price=0,
            icon_emoji='💧'
        ),

        # Обычная еда
        Item(
            name='Яблоко',
            description='Сочное яблоко. Полезно для здоровья.',
            item_type='food',
            rarity='common',
            health_effect=15,
            happiness_effect=10,
            coin_price=30,
            icon_emoji='🍎'
        ),
        Item(
            name='Морковка',
            description='Хрустящая морковка. Укрепляет интеллект!',
            item_type='food',
            rarity='common',
            health_effect=10,
            intelligence_effect=5,
            coin_price=25,
            icon_emoji='🥕'
        ),

        # Вкусняшки
        Item(
            name='Пицца',
            description='Вкусная пицца! Поднимает настроение.',
            item_type='food',
            rarity='uncommon',
            health_effect=20,
            happiness_effect=25,
            coin_price=50,
            icon_emoji='🍕'
        ),
        Item(
            name='Бургер',
            description='Сочный бургер. Много энергии!',
            item_type='food',
            rarity='uncommon',
            health_effect=25,
            happiness_effect=20,
            energy_effect=15,
            coin_price=75,
            icon_emoji='🍔'
        ),
        Item(
            name='Суши',
            description='Японская кухня. Делает умнее!',
            item_type='food',
            rarity='rare',
            health_effect=30,
            happiness_effect=30,
            intelligence_effect=15,
            coin_price=100,
            icon_emoji='🍱'
        ),
        Item(
            name='Торт',
            description='Праздничный торт! Максимум счастья.',
            item_type='food',
            rarity='rare',
            health_effect=15,
            happiness_effect=50,
            coin_price=150,
            icon_emoji='🎂'
        ),

        # Энергетики
        Item(
            name='Энергетик',
            description='Мощный энергетический напиток!',
            item_type='food',
            rarity='uncommon',
            energy_effect=40,
            coin_price=80,
            icon_emoji='⚡'
        ),
        Item(
            name='Кофе',
            description='Ароматный кофе. Бодрит и тонизирует.',
            item_type='food',
            rarity='common',
            energy_effect=20,
            intelligence_effect=5,
            coin_price=40,
            icon_emoji='☕'
        ),

        # Легендарная еда (только за кристаллы)
        Item(
            name='Золотое яблоко',
            description='Магическое яблоко. Восстанавливает ВСЁ!',
            item_type='food',
            rarity='legendary',
            health_effect=50,
            happiness_effect=50,
            intelligence_effect=25,
            energy_effect=50,
            crystal_price=200,
            icon_emoji='🍎'
        ),
        Item(
            name='Космобургер',
            description='Бургер из другого измерения. Дает x2 XP на час!',
            item_type='food',
            rarity='legendary',
            health_effect=40,
            happiness_effect=40,
            energy_effect=40,
            crystal_price=300,
            icon_emoji='🍔'
        ),
        Item(
            name='Радужный торт',
            description='Торт из радуги. Максимальное счастье!',
            item_type='food',
            rarity='legendary',
            health_effect=30,
            happiness_effect=100,
            crystal_price=250,
            icon_emoji='🌈'
        ),
    ]

    # === ЭКИПИРОВКА ===
    equipment = [
        # Оружие
        Item(
            name='Деревянный меч',
            description='Простой меч для начинающих.',
            item_type='equipment',
            rarity='common',
            stat_bonus='{"attack": 5}',
            coin_price=200,
            icon_emoji='🗡️'
        ),
        Item(
            name='Стальной меч',
            description='Крепкий меч из стали.',
            item_type='equipment',
            rarity='uncommon',
            stat_bonus='{"attack": 15}',
            coin_price=500,
            icon_emoji='⚔️'
        ),

        # Броня
        Item(
            name='Кожаная броня',
            description='Лёгкая броня для защиты.',
            item_type='equipment',
            rarity='common',
            stat_bonus='{"defense": 10}',
            coin_price=250,
            icon_emoji='🛡️'
        ),
        Item(
            name='Железная броня',
            description='Надёжная защита из железа.',
            item_type='equipment',
            rarity='uncommon',
            stat_bonus='{"defense": 20}',
            coin_price=600,
            icon_emoji='🛡️'
        ),

        # Аксессуары
        Item(
            name='Умная шляпа',
            description='Повышает интеллект питомца.',
            item_type='equipment',
            rarity='uncommon',
            stat_bonus='{"intelligence": 15}',
            coin_price=400,
            icon_emoji='🎩'
        ),
        Item(
            name='Крылья скорости',
            description='Дают невероятную ловкость.',
            item_type='equipment',
            rarity='rare',
            stat_bonus='{"speed": 25, "energy_regen": 5}',
            coin_price=800,
            icon_emoji='🪽'
        ),
    ]

    # === КОСМЕТИКА ===
    cosmetics = [
        Item(
            name='Солнечные очки',
            description='Стильные очки. Чисто для красоты!',
            item_type='cosmetic',
            rarity='common',
            coin_price=100,
            icon_emoji='🕶️'
        ),
        Item(
            name='Розовый шарфик',
            description='Милый шарфик розового цвета.',
            item_type='cosmetic',
            rarity='common',
            coin_price=150,
            icon_emoji='🧣'
        ),
        Item(
            name='Корона',
            description='Корона настоящего победителя!',
            item_type='cosmetic',
            rarity='legendary',
            crystal_price=500,
            icon_emoji='👑'
        ),
    ]

    # Добавляем всё в БД
    all_items = foods + equipment + cosmetics

    for item in all_items:
        db.add(item)

    db.commit()

    print(f'✅ Добавлено {len(all_items)} предметов!')
    print(f'   - Еды: {len(foods)}')
    print(f'   - Экипировки: {len(equipment)}')
    print(f'   - Косметики: {len(cosmetics)}')


if __name__ == '__main__':
    add_starter_items()