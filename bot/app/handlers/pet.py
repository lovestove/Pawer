from datetime import datetime, timedelta
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.core.database import Database
from app.states import UserStates
from app.keyboards import get_pet_keyboard, get_back_keyboard

router = Router()

# Настройки для питомца
HUNGER_DECAY_PER_HOUR = 5
THIRST_DECAY_PER_HOUR = 7
HAPPINESS_DECAY_PER_HOUR = 3
FEED_VALUE = 25
WATER_VALUE = 30
PLAY_VALUE = 20


def get_status_icon(value):
    if value > 80:
        return "😃"
    if value > 60:
        return "🙂"
    if value > 40:
        return "😐"
    if value > 20:
        return "😟"
    return "😭"


async def calculate_and_update_pet_stats(user_id: int, db: Database):
    pet = await db.get_pet(user_id)
    if not pet:
        return None

    last_updated = datetime.fromisoformat(pet["last_updated"])
    now = datetime.now()
    hours_passed = (now - last_updated).total_seconds() / 3600

    hunger = max(0, int(pet["hunger"] - hours_passed * HUNGER_DECAY_PER_HOUR))
    thirst = max(0, int(pet["thirst"] - hours_passed * THIRST_DECAY_PER_HOUR))
    happiness = max(0, int(pet["happiness"] - hours_passed * HAPPINESS_DECAY_PER_HOUR))

    await db.update_pet_stats(user_id, hunger, thirst, happiness)
    return await db.get_pet(user_id)


async def show_pet_status(message: Message, db: Database):
    pet = await calculate_and_update_pet_stats(message.from_user.id, db)
    if not pet:
        return

    text = f"""
🐾 **{pet['name']}** 🐾

{get_status_icon(pet['hunger'])} Голод: {pet['hunger']}/100
{get_status_icon(pet['thirst'])} Жажда: {pet['thirst']}/100
{get_status_icon(pet['happiness'])} Счастье: {pet['happiness']}/100

Что будем делать?
"""
    # Use answer for commands and edit_text for callbacks
    if isinstance(message, CallbackQuery):
        await message.message.edit_text(text, reply_markup=get_pet_keyboard())
    else:
        await message.answer(text, reply_markup=get_pet_keyboard())


@router.message(Command("pet"))
async def cmd_pet(message: Message, db: Database, state: FSMContext):
    """Команда /pet - управление питомцем"""
    pet = await db.get_pet(message.from_user.id)
    if pet:
        await show_pet_status(message, db)
    else:
        await message.answer("У вас еще нет питомца. Давайте создадим одного! Как вы его назовете?")
        await state.set_state(UserStates.waiting_for_pet_name)


@router.message(UserStates.waiting_for_pet_name, F.text)
async def process_pet_name(message: Message, db: Database, state: FSMContext):
    """Обработка имени питомца"""
    pet_name = message.text
    if len(pet_name) > 20:
        await message.answer("Слишком длинное имя! Попробуйте еще раз (не более 20 символов).")
        return

    await db.create_pet(message.from_user.id, pet_name)
    await state.clear()
    await message.answer(f"🎉 Поздравляем! У вас появился питомец по имени **{pet_name}**! 🎉\n\n"
                         f"Используйте команду /pet, чтобы проверить его состояние.",
                         reply_markup=get_back_keyboard(), parse_mode="Markdown")


@router.callback_query(F.data.startswith("pet_"))
async def handle_pet_action(callback: CallbackQuery, db: Database):
    action = callback.data.split("_")[1]
    user_id = callback.from_user.id

    pet = await calculate_and_update_pet_stats(user_id, db)
    if not pet:
        await callback.answer("Сначала создайте питомца!", show_alert=True)
        return

    hunger, thirst, happiness = pet["hunger"], pet["thirst"], pet["happiness"]
    alert_text = ""

    if action == "feed":
        hunger = min(100, hunger + FEED_VALUE)
        happiness = min(100, happiness + 5)
        alert_text = f"Вы покормили {pet['name']}! 🍖"
    elif action == "water":
        thirst = min(100, thirst + WATER_VALUE)
        happiness = min(100, happiness + 5)
        alert_text = f"Вы напоили {pet['name']}! 💧"
    elif action == "play":
        happiness = min(100, happiness + PLAY_VALUE)
        hunger = max(0, hunger - 5)
        thirst = max(0, thirst - 7)
        alert_text = f"Вы поиграли с {pet['name']}! 🎾"

    await db.update_pet_stats(user_id, hunger, thirst, happiness)
    await callback.answer(alert_text)
    await show_pet_status(callback, db)