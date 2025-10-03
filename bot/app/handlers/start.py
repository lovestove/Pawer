from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import re

from ..core.database import db
from ..keyboards.inline import get_main_menu, get_pet_type_keyboard
from ..states.user_states import PetCreation
from ..core.config import GameConfig

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Команда /start"""
    await state.clear()

    user = await db.get_user(message.from_user.id)

    # Проверка реферального кода
    referrer_id = None
    if message.text and len(message.text.split()) > 1:
        ref_code = message.text.split()[1]
        if ref_code.startswith('ref') and ref_code[3:].isdigit():
            referrer_id = int(ref_code[3:])

    # Создание пользователя
    if not user:
        await db.create_user(
            message.from_user.id,
            message.from_user.username or message.from_user.first_name,
            referrer_id
        )
        user = await db.get_user(message.from_user.id)

        # Приветственное сообщение
        welcome_text = (
            "✨ <b>Добро пожаловать в мир Pawer!</b> ✨\n\n"
            "🐾 Здесь тебя ждёт невероятное приключение с твоим виртуальным питомцем!\n\n"
            "💝 <b>Что тебя ждёт:</b>\n"
            "🍎 Корми своего питомца вкусной едой\n"
            "⚽ Играй с ним в весёлые игры\n"
            "🛁 Ухаживай и следи за чистотой\n"
            "✨ Кастомизируй внешность\n"
            "🎁 Получай награды каждый день\n"
            "👥 Приглашай друзей и получай бонусы!\n\n"
            "🎉 Начни своё путешествие с создания питомца!"
        )

        await message.answer(
            welcome_text,
            reply_markup=get_main_menu(has_pet=False)
        )
    else:
        # Обновление серии дней
        streak, reward = await db.update_streak(message.from_user.id)

        pet = await db.get_active_pet(message.from_user.id)

        if pet:
            if reward > 0:
                streak_text = (
                    f"🔥 <b>Серия входов: {streak} дней!</b>\n"
                    f"🎁 Получено: {reward} монет\n\n"
                )

                if streak % 7 == 0:
                    streak_text += "🌟 <b>Недельный бонус! +5 гемов!</b>\n\n"
                elif streak % 3 == 0:
                    streak_text += "⭐ <b>Бонус за 3 дня! +50 монет!</b>\n\n"
            else:
                streak_text = ""

            # Статус питомца
            status = get_pet_status_emoji(pet)

            text = (
                f"{streak_text}"
                f"🐾 <b>С возвращением!</b>\n\n"
                f"💝 Твой питомец <b>{pet['name']}</b> {GameConfig.PET_TYPES[pet['pet_type']]['emoji']} ждёт тебя!\n\n"
                f"📊 <b>Статус:</b>\n"
                f"{status}"
            )
        else:
            text = "🐾 <b>Добро пожаловать!</b>\n\nСоздай своего первого питомца!"

        await message.answer(
            text,
            reply_markup=get_main_menu(has_pet=bool(pet))
        )


@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()

    pet = await db.get_active_pet(callback.from_user.id)

    if pet:
        status = get_pet_status_emoji(pet)
        text = (
            f"🐾 <b>Главное меню</b>\n\n"
            f"💝 <b>{pet['name']}</b> {GameConfig.PET_TYPES[pet['pet_type']]['emoji']}\n"
            f"⭐ Уровень: {pet['level']}\n\n"
            f"📊 <b>Статус:</b>\n"
            f"{status}"
        )
    else:
        text = "🐾 <b>Главное меню</b>"

    await callback.message.edit_text(
        text,
        reply_markup=get_main_menu(has_pet=bool(pet))
    )


@router.callback_query(F.data == "create_pet")
async def callback_create_pet(callback: CallbackQuery, state: FSMContext):
    """Начало создания питомца"""
    await state.set_state(PetCreation.choosing_name)

    await callback.message.edit_text(
        "✨ <b>Создание питомца</b>\n\n"
        "🐾 Придумай имя для своего нового друга!\n\n"
        "💡 <i>Имя может содержать буквы, цифры и пробелы (до 20 символов)</i>",
    )
    await callback.answer()


@router.message(PetCreation.choosing_name)
async def process_pet_name(message: Message, state: FSMContext):
    """Обработка имени питомца"""
    name = message.text.strip()

    # Валидация имени
    if not name or len(name) > 20:
        await message.answer(
            "❌ Имя должно быть от 1 до 20 символов. Попробуй ещё раз!"
        )
        return

    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9\s]+$', name):
        await message.answer(
            "❌ Имя может содержать только буквы, цифры и пробелы. Попробуй ещё раз!"
        )
        return

    # Сохраняем имя
    await state.update_data(name=name)
    await state.set_state(PetCreation.choosing_type)

    # Получаем купленные яйца
    owned_eggs = await db.get_owned_eggs(message.from_user.id)
    owned_eggs.append('basic')  # Базовый всегда доступен

    await message.answer(
        f"✅ Отличное имя - <b>{name}</b>!\n\n"
        f"🥚 Теперь выбери яйцо для своего питомца:\n\n"
        f"💡 <i>Базовый котик доступен бесплатно, остальные яйца можно купить в магазине</i>",
        reply_markup=get_pet_type_keyboard(owned_eggs)
    )


@router.callback_query(F.data.startswith("pettype_"))
async def callback_choose_pet_type(callback: CallbackQuery, state: FSMContext):
    """Выбор типа питомца"""
    pet_type = callback.data.split("_")[1]
    data = await state.get_data()
    name = data.get('name')

    if not name:
        await callback.answer("❌ Ошибка! Начни сначала с /start")
        return

    # Создаём питомца
    pet_id = await db.create_pet(callback.from_user.id, name, pet_type)
    await state.clear()

    info = GameConfig.PET_TYPES[pet_type]

    # Красивое сообщение о создании
    await callback.message.delete()

    celebration_msg = await callback.message.answer(
        f"🎉✨🎊\n\n"
        f"<b>Поздравляем!</b>\n\n"
        f"Твой новый друг {info['emoji']} <b>{name}</b> появился на свет!\n\n"
        f"💝 Заботься о нём каждый день\n"
        f"🎮 Играй и веселись вместе\n"
        f"📈 Развивайся и получай награды\n\n"
        f"✨ <i>Открой приложение, чтобы увидеть своего питомца!</i>"
    )

    # Даём время прочитать
    import asyncio
    await asyncio.sleep(3)

    await celebration_msg.edit_text(
        f"🐾 <b>Твой питомец готов к приключениям!</b>\n\n"
        f"{info['emoji']} <b>{name}</b>\n"
        f"⭐ Уровень: 1\n\n"
        f"📊 <b>Все параметры:</b>\n"
        f"🍖 Голод: 100%\n"
        f"💖 Счастье: 100%\n"
        f"⚡ Энергия: 100%\n"
        f"✨ Чистота: 100%\n\n"
        f"🎁 Стартовый бонус:\n"
        f"💰 100 монет\n"
        f"💎 5 гемов",
        reply_markup=get_main_menu(has_pet=True)
    )

    await callback.answer("🎉 Питомец создан!")


@router.callback_query(F.data == "profile")
async def callback_profile(callback: CallbackQuery):
    """Профиль пользователя"""
    user = await db.get_user(callback.from_user.id)
    pet = await db.get_active_pet(callback.from_user.id)

    if not user or not pet:
        await callback.answer("❌ Ошибка загрузки профиля")
        return

    # Реферальный код
    ref_code = f"ref{callback.from_user.id}"

    info = GameConfig.PET_TYPES[pet['pet_type']]
    exp_needed = GameConfig.exp_for_level(pet['level'])
    exp_progress = (pet['exp'] / exp_needed * 100) if exp_needed > 0 else 0

    text = (
        f"👤 <b>Профиль</b>\n\n"
        f"🆔 ID: <code>{callback.from_user.id}</code>\n"
        f"👤 Имя: {callback.from_user.first_name}\n\n"
        f"💰 Монеты: <b>{user['coins']}</b>\n"
        f"💎 Гемы: <b>{user['gems']}</b>\n\n"
        f"🔥 Серия дней: <b>{user['streak_days']}</b>\n"
        f"👥 Приглашено друзей: <b>{user['referral_count']}</b>\n\n"
        f"🐾 <b>Активный питомец:</b>\n"
        f"{info['emoji']} {pet['name']}\n"
        f"⭐ Уровень: {pet['level']}\n"
        f"📊 Опыт: {pet['exp']}/{exp_needed} ({exp_progress:.0f}%)\n\n"
        f"🔗 Твой реферальный код:\n"
        f"<code>{ref_code}</code>"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_main_menu(has_pet=True)
    )
    await callback.answer()


def get_pet_status_emoji(pet: dict) -> str:
    """Получить статус питомца с эмодзи"""

    def get_bar(value: int) -> str:
        if value >= 80:
            return "🟢"
        elif value >= 50:
            return "🟡"
        elif value >= 30:
            return "🟠"
        else:
            return "🔴"

    return (
        f"{get_bar(pet['hunger'])} Голод: {pet['hunger']}%\n"
        f"{get_bar(pet['happiness'])} Счастье: {pet['happiness']}%\n"
        f"{get_bar(pet['energy'])} Энергия: {pet['energy']}%\n"
        f"{get_bar(pet['hygiene'])} Чистота: {pet['hygiene']}%"
    )