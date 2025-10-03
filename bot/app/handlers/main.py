# """
# Главный обработчик команд бота
# """
# from aiogram import Router, F
# from aiogram.filters import CommandStart, Command
# from aiogram.types import Message, CallbackQuery
# from aiogram.fsm.context import FSMContext
#
# from app.keyboards.inline import get_main_menu, get_pet_actions_kb
# from app.core.database import Database
# from app.keyboards.webapp import get_webapp_button
#
# router = Router()
#
#
# @router.message(CommandStart())
# async def cmd_start(message: Message, db: Database):
#     """Команда /start"""
#     user_id = message.from_user.id
#
#     # Проверяем, есть ли у пользователя питомец
#     pet = await db.get_pet(user_id)
#
#     if pet:
#         await message.answer(
#             f"🌟 С возвращением, дорогой!\n\n"
#             f"Твой питомец {pet['name']} очень скучал! 💚\n"
#             f"Открой приложение и позаботься о нём!",
#             reply_markup=get_webapp_button()
#         )
#     else:
#         await message.answer(
#             f"👋 Привет, {message.from_user.first_name}!\n\n"
#             f"Я Pawer - твой персональный помощник по уходу за цифровым питомцем! 🐾\n\n"
#             f"Заводи своего питомца, заботься о нём, играй и зарабатывай монеты! 🪙\n\n"
#             f"Открывай приложение и начинай своё приключение! ✨",
#             reply_markup=get_webapp_button()
#         )
#
#
# @router.message(Command("app"))
# async def cmd_app(message: Message):
#     """Команда /app - открыть Mini App"""
#     await message.answer(
#         "🐾 Открой приложение, чтобы позаботиться о своём питомце!",
#         reply_markup=get_webapp_button()
#     )
#
#
# @router.message(Command("stats"))
# async def cmd_stats(message: Message, db: Database):
#     """Статистика питомца"""
#     user_id = message.from_user.id
#     pet = await db.get_pet(user_id)
#
#     if not pet:
#         await message.answer(
#             "У тебя ещё нет питомца, милый! 😊\n"
#             "Открой приложение и заведи своего первого друга!",
#             reply_markup=get_webapp_button()
#         )
#         return
#
#     stats = pet['stats']
#     health_bar = create_bar(stats['health'])
#     happiness_bar = create_bar(stats['happiness'])
#     energy_bar = create_bar(stats['energy'])
#     hunger_bar = create_bar(stats['hunger'])
#
#     await message.answer(
#         f"🐾 <b>{pet['name']}</b> {pet['emoji']}\n\n"
#         f"📊 <b>Статистика:</b>\n"
#         f"├ ❤️ Здоровье: {health_bar} {stats['health']:.0f}%\n"
#         f"├ 😊 Счастье: {happiness_bar} {stats['happiness']:.0f}%\n"
#         f"├ ⚡ Энергия: {energy_bar} {stats['energy']:.0f}%\n"
#         f"└ 🍖 Сытость: {hunger_bar} {stats['hunger']:.0f}%\n\n"
#         f"💎 <b>Уровень:</b> {pet['level']}\n"
#         f"✨ <b>Опыт:</b> {pet['xp']}/{pet['level'] * 100}\n"
#         f"🪙 <b>Монеты:</b> {pet['coins']}\n\n"
#         f"🔥 <b>Серия:</b> {pet.get('streak', 1)} дней подряд",
#         parse_mode="HTML",
#         reply_markup=get_webapp_button()
#     )
#
#
# @router.message(Command("shop"))
# async def cmd_shop(message: Message):
#     """Открыть магазин"""
#     await message.answer(
#         "🏪 <b>Магазин Pawer</b>\n\n"
#         "Открой приложение, чтобы купить вкусности и предметы для своего питомца! 💚",
#         parse_mode="HTML",
#         reply_markup=get_webapp_button()
#     )
#
#
# @router.message(Command("help"))
# async def cmd_help(message: Message):
#     """Помощь"""
#     await message.answer(
#         "❓ <b>Как играть:</b>\n\n"
#         "🐾 <b>Основы:</b>\n"
#         "• Заводи питомца и дай ему имя\n"
#         "• Корми, играй, мой и укладывай спать\n"
#         "• Следи за статами: здоровье, счастье, энергия, сытость\n\n"
#         "🎮 <b>Действия:</b>\n"
#         "• 🍖 Кормить - восстанавливает сытость\n"
#         "• 🎾 Играть - повышает счастье\n"
#         "• 🛁 Мыть - улучшает здоровье\n"
#         "• 😴 Спать - восстанавливает энергию\n\n"
#         "💰 <b>Монетизация:</b>\n"
#         "• Зарабатывай монеты за уход\n"
#         "• Покупай еду и предметы в магазине\n"
#         "• Получай бонусы за ежедневный вход\n\n"
#         "⚠️ <b>Важно:</b>\n"
#         "• Статы питомца снижаются со временем\n"
#         "• Не забывай заботиться о нём каждый день!\n"
#         "• Чем выше уровень - тем больше возможностей\n\n"
#         "💚 Твой питомец - это твоя ответственность и радость!",
#         parse_mode="HTML",
#         reply_markup=get_webapp_button()
#     )
#
#
# @router.message(Command("daily"))
# async def cmd_daily(message: Message, db: Database):
#     """Ежедневная награда"""
#     user_id = message.from_user.id
#     pet = await db.get_pet(user_id)
#
#     if not pet:
#         await message.answer(
#             "У тебя ещё нет питомца, дорогой! 😊",
#             reply_markup=get_webapp_button()
#         )
#         return
#
#     # Проверяем, можно ли получить награду
#     can_claim, bonus = await db.check_daily_reward(user_id)
#
#     if not can_claim:
#         await message.answer(
#             "⏰ Ты уже получил свою ежедневную награду!\n"
#             "Приходи завтра за новым бонусом! 💚"
#         )
#         return
#
#     # Начисляем награду
#     await db.claim_daily_reward(user_id, bonus)
#
#     await message.answer(
#         f"🎁 <b>Ежедневная награда!</b>\n\n"
#         f"Получено: +{bonus} 🪙\n"
#         f"🔥 Серия: {pet.get('streak', 1)} дней\n\n"
#         f"Продолжай заходить каждый день для больших бонусов! 💚",
#         parse_mode="HTML"
#     )
#
#
# @router.message(Command("leaderboard"))
# async def cmd_leaderboard(message: Message, db: Database):
#     """Таблица лидеров"""
#     top_users = await db.get_leaderboard(limit=10)
#
#     if not top_users:
#         await message.answer("Пока нет данных для рейтинга 😊")
#         return
#
#     text = "🏆 <b>Топ-10 владельцев питомцев</b>\n\n"
#
#     medals = ["🥇", "🥈", "🥉"]
#     for i, user in enumerate(top_users, 1):
#         medal = medals[i - 1] if i <= 3 else f"{i}."
#         text += f"{medal} <b>{user['name']}</b> • Ур.{user['level']} • {user['coins']}🪙\n"
#
#     await message.answer(text, parse_mode="HTML")
#
# 
# def create_bar(value: float, length: int = 10) -> str:
#     """Создание визуального бара для статов"""
#     filled = int((value / 100) * length)
#     empty = length - filled
#
#     if value >= 70:
#         return "🟩" * filled + "⬜" * empty
#     elif value >= 40:
#         return "🟨" * filled + "⬜" * empty
#     else:
#         return "🟥" * filled + "⬜" * empty
#
#
# @router.message(F.text)
# async def handle_text(message: Message):
#     """Обработка текстовых сообщений"""
#     await message.answer(
#         "Я понимаю только команды, дорогой! 😊\n"
#         "Используй /help чтобы узнать что я умею, или открой приложение!",
#         reply_markup=get_webapp_button()
#     )