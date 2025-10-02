import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter

from app.states import UserStates
from app.keyboards import get_back_keyboard

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "feedback")
async def callback_feedback(callback: CallbackQuery, state: FSMContext):
    """Начать процесс обратной связи"""
    await callback.message.edit_text(
        "💬 <b>Обратная связь</b>\n\nНапиши свой вопрос или предложение:",
        parse_mode="HTML"
    )
    await state.set_state(UserStates.waiting_for_feedback)
    await callback.answer()


@router.message(StateFilter(UserStates.waiting_for_feedback))
async def process_feedback(message: Message, state: FSMContext):
    """Обработка обратной связи"""
    feedback_text = message.text

    await message.answer(
        "✅ <b>Спасибо за обратную связь!</b>\n\nМы обязательно рассмотрим твоё сообщение.",
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )

    logger.info(f"Feedback from {message.from_user.id}: {feedback_text}")
    await state.clear()