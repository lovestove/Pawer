from aiogram import Router, F
import aiogram.types as types
from aiogram.types import Message, CallbackQuery, WebAppInfo
import aiogram.filters as filters
from keyboards.inline import inline_start_bot, inline_main_menu, inline_create_pet
from database import crud
from database.engine import get_db

router = Router()


@router.message(filters.CommandStart())
async def cmd_start(message: Message):
    """Команда /start - начало работы с ботом"""

    # Получаем или создаем пользователя
    db = get_db()
    user = crud.get_or_create_user(
        db,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )

    # Проверяем, есть ли у пользователя питомцы
    pets = crud.get_user_pets(db, user.id)

    if not pets:
        # Если питомцев нет - предлагаем создать
        await message.answer(
            f"""
🌟 <b>Привет, {message.from_user.first_name}!</b>

Добро пожаловать в <b>Pawer</b> - мир цифровых питомцев!

Здесь ты сможешь:
🐱 Вырастить своего уникального питомца
💖 Заботиться о нём и играть вместе
⚔️ Сражаться с другими игроками
🎨 Кастомизировать внешний вид
🏆 Достигать невероятных высот!

<b>Давай создадим твоего первого питомца!</b>
            """,
            reply_markup=inline_start_bot(),
            parse_mode='HTML'
        )
    else:
        # Если питомец уже есть - показываем главное меню
        pet = pets[0]  # Берем первого питомца
        await message.answer(
            f"""
Привет снова, {message.from_user.first_name}! 👋

Твой питомец <b>{pet.name}</b> ждёт тебя!
Уровень: {pet.level} | Здоровье: {int(pet.health)}❤️
            """,
            reply_markup=inline_main_menu(),
            parse_mode='HTML'
        )


@router.callback_query(F.data == 'create_pet')
async def start_pet_creation(callback: CallbackQuery):
    """Начало создания питомца"""
    await callback.message.edit_text(
        """
🎨 <b>Создание питомца - Шаг 1/3</b>

<b>Выбери вид своего питомца:</b>

🐱 <b>Киберкот</b> - ловкий и быстрый
🐉 <b>Дракончик</b> - сильный и храбрый  
☁️ <b>Облачко</b> - милое и доброе
🤖 <b>Робопёс</b> - умный и верный
        """,
        reply_markup=inline_create_pet(),
        parse_mode='HTML'
    )


@router.callback_query(F.data.startswith('species_'))
async def choose_species(callback: CallbackQuery):
    """Выбор вида питомца"""
    species = callback.data.split('_')[1]

    # Сохраняем выбор во временное хранилище (в реальности лучше использовать FSM)
    # Пока просто создаем питомца сразу

    species_emojis = {
        'cyber_cat': '🐱',
        'dragon': '🐉',
        'cloud': '☁️',
        'robo_dog': '🤖'
    }

    species_names = {
        'cyber_cat': 'Киберкот',
        'dragon': 'Дракончик',
        'cloud': 'Облачко',
        'robo_dog': 'Робопёс'
    }

    await callback.message.edit_text(
        f"""
✨ <b>Отличный выбор!</b>

Твой {species_names[species]} {species_emojis[species]} готов к жизни!

<b>Как назовём питомца?</b>
Напиши имя в чат (например: Барсик, Дракоша, Пушок)
        """,
        parse_mode='HTML'
    )

    # Сохраняем выбор в callback data для следующего шага
    await callback.answer()


@router.message(F.text, ~filters.Command())
async def handle_pet_name(message: Message):
    """Обработка имени питомца"""
    db = get_db()
    user = crud.get_or_create_user(
        db,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )

    # Проверяем, есть ли уже питомец
    pets = crud.get_user_pets(db, user.id)

    if pets:
        # Если питомец уже есть, показываем кнопку Mini App
        await message.answer(
            "Используй кнопку ниже для управления питомцем! 👇",
            reply_markup=inline_main_menu()
        )
        return

    # Создаем нового питомца с именем из сообщения
    pet_name = message.text[:20]  # Ограничиваем длину имени

    # Создаем питомца (по умолчанию киберкот)
    pet = crud.create_pet(
        db,
        owner_id=user.id,
        name=pet_name,
        species='cyber_cat',
        personality='playful',
        color='blue',
        pattern='solid'
    )

    # Даем стартовые предметы
    # TODO: добавить стартовую еду в инвентарь

    await message.answer(
        f"""
🎉 <b>Поздравляю!</b>

Твой питомец <b>{pet.name}</b> родился! 🐱✨

<b>Стартовые характеристики:</b>
❤️ Здоровье: {int(pet.health)}
😊 Настроение: {int(pet.happiness)}
🧠 Интеллект: {int(pet.intelligence)}
⚡ Энергия: {int(pet.energy)}

<b>Ты получил:</b>
🪙 100 монет
💎 10 кристаллов
🍞 3x Хлеб (стартовая еда)

Открой Mini App чтобы начать заботиться о питомце! 👇
        """,
        reply_markup=inline_main_menu(),
        parse_mode='HTML'
    )


@router.callback_query(F.data == 'main_menu')
async def show_main_menu(callback: CallbackQuery):
    """Показать главное меню с Mini App"""
    db = get_db()
    user = crud.get_or_create_user(
        db,
        telegram_id=callback.from_user.id
    )

    pets = crud.get_user_pets(db, user.id)

    if not pets:
        await callback.message.edit_text(
            "У тебя пока нет питомца! Создай его:",
            reply_markup=inline_start_bot()
        )
        return

    pet = pets[0]

    await callback.message.edit_text(
        f"""
🏠 <b>Главное меню</b>

<b>{pet.name}</b> - Уровень {pet.level}

❤️ Здоровье: {int(pet.health)}
😊 Настроение: {int(pet.happiness)}
⚡ Энергия: {int(pet.energy)}

💰 Твои ресурсы:
🪙 {user.coins} монет
💎 {user.crystals} кристаллов

Открой приложение для полного управления! 👇
        """,
        reply_markup=inline_main_menu(),
        parse_mode='HTML'
    )
    await callback.answer()


@router.callback_query(F.data == 'quick_feed')
async def quick_feed(callback: CallbackQuery):
    """Быстрое кормление (хлебом)"""
    db = get_db()
    user = crud.get_or_create_user(db, telegram_id=callback.from_user.id)
    pets = crud.get_user_pets(db, user.id)

    if not pets:
        await callback.answer("Сначала создай питомца!", show_alert=True)
        return

    pet = pets[0]

    # Даем базовую еду (хлеб: +10 здоровье, +5 счастье)
    updated_pet = crud.update_pet_stats(
        db,
        pet.id,
        health=10,
        happiness=5
    )

    # Даем XP
    xp_result = crud.add_pet_xp(db, pet.id, 10)

    msg = f"🍞 {pet.name} покушал!\n"
    if xp_result['leveled_up']:
        msg += f"🎉 УРОВЕНЬ ПОВЫШЕН до {xp_result['pet'].level}!"

    await callback.answer(msg, show_alert=True)

    # Обновляем сообщение
    await callback.message.edit_text(
        f"""
🏠 <b>Главное меню</b>

<b>{updated_pet.name}</b> - Уровень {updated_pet.level}

❤️ Здоровье: {int(updated_pet.health)}
😊 Настроение: {int(updated_pet.happiness)}
⚡ Энергия: {int(updated_pet.energy)}

💰 Твои ресурсы:
🪙 {user.coins} монет
💎 {user.crystals} кристаллов
        """,
        reply_markup=inline_main_menu(),
        parse_mode='HTML'
    )


@router.callback_query(F.data == 'quick_play')
async def quick_play(callback: CallbackQuery):
    """Быстрая игра"""
    db = get_db()
    user = crud.get_or_create_user(db, telegram_id=callback.from_user.id)
    pets = crud.get_user_pets(db, user.id)

    if not pets:
        await callback.answer("Сначала создай питомца!", show_alert=True)
        return

    pet = pets[0]

    # Играем
    result = crud.play_with_pet(db, pet.id, 'simple')

    if not result['success']:
        await callback.answer(result['message'], show_alert=True)
        return

    msg = f"🎮 {result['message']}\n+{result['xp_gained']} XP"
    if result['leveled_up']:
        msg += f"\n🎉 УРОВЕНЬ ПОВЫШЕН!"

    await callback.answer(msg, show_alert=True)

    # Обновляем данные
    updated_pet = crud.get_pet_by_id(db, pet.id)

    await callback.message.edit_text(
        f"""
🏠 <b>Главное меню</b>

<b>{updated_pet.name}</b> - Уровень {updated_pet.level}

❤️ Здоровье: {int(updated_pet.health)}
😊 Настроение: {int(updated_pet.happiness)}
⚡ Энергия: {int(updated_pet.energy)}

💰 Твои ресурсы:
🪙 {user.coins} монет
💎 {user.crystals} кристаллов
        """,
        reply_markup=inline_main_menu(),
        parse_mode='HTML'
    )


@router.callback_query(F.data == 'pet_stats')
async def show_pet_stats(callback: CallbackQuery):
    """Показать подробную статистику питомца"""
    db = get_db()
    user = crud.get_or_create_user(db, telegram_id=callback.from_user.id)
    pets = crud.get_user_pets(db, user.id)

    if not pets:
        await callback.answer("У тебя нет питомца!", show_alert=True)
        return

    pet = pets[0]
    skills = crud.get_pet_skills(db, pet.id)

    # Вычисляем прогресс до следующего уровня
    xp_needed = pet.level * 100
    xp_progress = int((pet.xp / xp_needed) * 100)

    skills_text = ""
    if skills:
        skills_text = "\n\n<b>🎯 Навыки:</b>\n"
        for skill in skills[:5]:  # Показываем первые 5
            skills_text += f"• {skill.skill_name} (ур. {skill.level})\n"

    await callback.message.edit_text(
        f"""
📊 <b>Статистика питомца</b>

<b>Имя:</b> {pet.name}
<b>Вид:</b> {pet.species}
<b>Характер:</b> {pet.personality}

<b>⭐ Уровень {pet.level}</b>
Опыт: {pet.xp}/{xp_needed} ({xp_progress}%)

<b>📈 Характеристики:</b>
❤️ Здоровье: {int(pet.health)}/100
😊 Настроение: {int(pet.happiness)}/100
🧠 Интеллект: {int(pet.intelligence)}/100
⚡ Энергия: {int(pet.energy)}/100

<b>🏆 Достижения:</b>
🎮 Игр сыграно: {pet.total_games_played}
⚔️ Побед в боях: {pet.battles_won}
💀 Поражений: {pet.battles_lost}

<b>🎭 Эволюция:</b>
Стадия: {pet.evolution_stage}/4
Путь: {pet.evolution_path}
{skills_text}

<i>Питомец с тобой уже {(callback.message.date - pet.created_at).days} дней</i>
        """,
        reply_markup=inline_main_menu(),
        parse_mode='HTML'
    )
    await callback.answer()


@router.message(filters.Command(commands=['stats']))
async def cmd_stats(message: Message):
    """Команда для просмотра статистики"""
    db = get_db()
    user = crud.get_or_create_user(
        db,
        telegram_id=message.from_user.id
    )

    pets = crud.get_user_pets(db, user.id)

    if not pets:
        await message.answer(
            "У тебя пока нет питомца! Используй /start чтобы создать.",
            reply_markup=inline_start_bot()
        )
        return

    pet = pets[0]

    await message.answer(
        f"""
📊 <b>Статистика</b>

<b>👤 Игрок:</b>
Имя: {user.first_name}
Стрик логинов: {user.login_streak} дней 🔥
🪙 Монеты: {user.coins}
💎 Кристаллы: {user.crystals}

<b>🐾 Питомец: {pet.name}</b>
Уровень: {pet.level}
❤️ {int(pet.health)} | 😊 {int(pet.happiness)} | ⚡ {int(pet.energy)}

Используй Mini App для полного управления! 👇
        """,
        reply_markup=inline_main_menu(),
        parse_mode='HTML'
    )


@router.message(filters.Command(commands=['help']))
async def cmd_help(message: Message):
    """Справка по командам"""
    await message.answer(
        """
<b>📖 Справка по Pawer</b>

<b>Основные команды:</b>
/start - Начать или показать меню
/stats - Посмотреть статистику
/help - Эта справка

<b>🎮 Как играть:</b>

1️⃣ <b>Заботься о питомце</b>
   • Корми его регулярно 🍕
   • Играй с ним 🎮
   • Давай отдыхать 😴

2️⃣ <b>Качай уровень</b>
   • Выполняй действия → получай XP
   • Повышай уровень → открывай эволюции

3️⃣ <b>Развивай питомца</b>
   • Учи новым навыкам
   • Экипируй предметы
   • Кастомизируй внешний вид

4️⃣ <b>Сражайся и побеждай</b>
   • PvP бои с другими игроками
   • Турниры с крутыми призами
   • Босс-рейды вместе с друзьями

<b>💡 Советы:</b>
• Заходи каждый день для бонусов
• Не забывай кормить питомца
• Участвуй в ивентах для наград

<b>Открой Mini App для полного функционала! 👇</b>
        """,
        reply_markup=inline_main_menu(),
        parse_mode='HTML'
    )