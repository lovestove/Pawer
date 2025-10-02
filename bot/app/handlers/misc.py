from aiogram import Router, F
from aiogram.types import Message

from app.keyboards import get_back_keyboard

router = Router()


@router.message(F.text)
async def handle_text(message: Message):
    """Обработка текстовых сообщений"""
    await message.answer(
        f"Ты написал: {message.text}\n\nИспользуй /start для главного меню",
        reply_markup=get_back_keyboard()
    )


@router.message(F.photo)
async def handle_photo(message: Message):
    """Обработка фото"""
    await message.answer(
        "📸 Получил фото! В будущем здесь будет обработка изображений.",
        reply_markup=get_back_keyboard()
    )


@router.message(F.document)
async def handle_document(message: Message):
    """Обработка документов"""
    await message.answer(
        "📄 Получил документ! Пока не обрабатываю файлы.",
        reply_markup=get_back_keyboard()
    )