from aiogram import Router, F
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..core.database import db
from ..keyboards.inline import (
    get_coin_packages_keyboard, get_gem_packages_keyboard,
    get_payment_method_keyboard
)
from ..core.config import GameConfig, settings

router = Router()


@router.callback_query(F.data == "buy_coins")
async def callback_buy_coins(callback: CallbackQuery):
    """Покупка монет"""
    text = (
        f"💰 <b>Магазин монет</b>\n\n"
        f"Выбери пакет монет для покупки:\n\n"
        f"✨ Чем больше пакет, тем выгоднее цена!"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_coin_packages_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "buy_gems")
async def callback_buy_gems(callback: CallbackQuery):
    """Покупка гемов"""
    text = (
        f"💎 <b>Магазин гемов</b>\n\n"
        f"Выбери пакет гемов для покупки:\n\n"
        f"💎 Гемы - премиальная валюта для особых покупок!"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_gem_packages_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("coinpkg_"))
async def callback_coin_package(callback: CallbackQuery):
    """Выбор пакета монет"""
    package_index = int(callback.data.split("_")[1])
    package = GameConfig.COIN_PACKAGES[package_index]

    bonus = int(package['coins'] * package['bonus'] / 100) if package['bonus'] > 0 else 0
    total_coins = package['coins'] + bonus

    text = (
        f"💰 <b>Пакет монет</b>\n\n"
        f"🪙 Монет: <b>{package['coins']}</b>\n"
    )

    if bonus > 0:
        text += f"🎁 Бонус: <b>+{bonus}</b> ({package['bonus']}%)\n"
        text += f"📦 Всего: <b>{total_coins}</b> монет\n\n"
    else:
        text += f"\n"

    text += (
        f"💵 Цена: <b>{package['price_rub']}₽</b>\n"
        f"⭐ В звёздах: <b>{package['price_stars']}</b> Stars\n\n"
        f"Выбери способ оплаты:"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_payment_method_keyboard('coin', package_index)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("gempkg_"))
async def callback_gem_package(callback: CallbackQuery):
    """Выбор пакета гемов"""
    package_index = int(callback.data.split("_")[1])
    package = GameConfig.GEM_PACKAGES[package_index]

    text = (
        f"💎 <b>Пакет гемов</b>\n\n"
        f"💎 Гемов: <b>{package['gems']}</b>\n\n"
        f"💵 Цена: <b>{package['price_rub']}₽</b>\n"
        f"⭐ В звёздах: <b>{package['price_stars']}</b> Stars\n\n"
        f"Выбери способ оплаты:"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_payment_method_keyboard('gem', package_index)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pay_"))
async def callback_payment_method(callback: CallbackQuery):
    """Обработка выбора метода оплаты"""
    parts = callback.data.split("_")
    method = parts[1]  # stars, yoomoney, sbp
    package_type = parts[2]  # coin или gem
    package_index = int(parts[3])

    if package_type == 'coin':
        package = GameConfig.COIN_PACKAGES[package_index]
        bonus = int(package['coins'] * package['bonus'] / 100) if package['bonus'] > 0 else 0
        total_amount = package['coins'] + bonus
        currency_emoji = "💰"
        currency_name = "монет"
    else:
        package = GameConfig.GEM_PACKAGES[package_index]
        total_amount = package['gems']
        currency_emoji = "💎"
        currency_name = "гемов"

    if method == "stars":
        # Оплата через Telegram Stars
        if not settings.STARS_ENABLED:
            await callback.answer("❌ Оплата Stars временно недоступна", show_alert=True)
            return

        try:
            # Создаём инвойс для Stars
            await callback.message.answer_invoice(
                title=f"Пакет {currency_name}",
                description=f"{currency_emoji} {total_amount} {currency_name}",
                payload=f"{package_type}_{package_index}",
                provider_token="",  # Пустой для Stars
                currency="XTR",
                prices=[LabeledPrice(label=f"{total_amount} {currency_name}", amount=package['price_stars'])],
            )
            await callback.answer("✨ Инвойс отправлен!")
        except Exception as e:
            await callback.answer(f"❌ Ошибка создания инвойса: {str(e)}", show_alert=True)

    elif method == "yoomoney":
        # ЮMoney
        if not settings.YOOMONEY_TOKEN:
            await callback.answer("❌ ЮMoney временно недоступно", show_alert=True)
            return

        # Здесь должна быть интеграция с ЮMoney API
        payment_url = f"https://yoomoney.ru/to/{settings.YOOMONEY_WALLET}"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить через ЮMoney", url=payment_url)],
            [InlineKeyboardButton(text="◀️ Назад", callback_data=f"buy_{package_type}s")]
        ])

        text = (
            f"💳 <b>Оплата через ЮMoney</b>\n\n"
            f"{currency_emoji} {total_amount} {currency_name}\n"
            f"💵 Сумма: <b>{package['price_rub']}₽</b>\n\n"
            f"После оплаты отправьте скриншот чека администратору:\n"
            f"@your_admin\n\n"
            f"⚠️ В комментарии к платежу укажите:\n"
            f"<code>{callback.from_user.id}_{package_type}_{package_index}</code>"
        )

        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()

    elif method == "sbp":
        # СБП
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data=f"buy_{package_type}s")]
        ])

        text = (
            f"🏦 <b>Оплата через СБП</b>\n\n"
            f"{currency_emoji} {total_amount} {currency_name}\n"
            f"💵 Сумма: <b>{package['price_rub']}₽</b>\n\n"
            f"Для оплаты через СБП свяжитесь с администратором:\n"
            f"@your_admin\n\n"
            f"Укажите ваш ID: <code>{callback.from_user.id}</code>\n"
            f"И код пакета: <code>{package_type}_{package_index}</code>"
        )

        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    """Обработка pre-checkout для Stars"""
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    """Обработка успешного платежа"""
    payment = message.successful_payment
    payload = payment.invoice_payload

    try:
        parts = payload.split("_")
        package_type = parts[0]
        package_index = int(parts[1])

        if package_type == 'coin':
            package = GameConfig.COIN_PACKAGES[package_index]
            bonus = int(package['coins'] * package['bonus'] / 100) if package['bonus'] > 0 else 0
            total_coins = package['coins'] + bonus

            await db.add_coins(message.from_user.id, total_coins)
            await db.add_transaction(
                message.from_user.id,
                'purchase',
                payment.total_amount,
                'stars',
                f"Куплено {total_coins} монет"
            )

            await message.answer(
                f"🎉 <b>Покупка успешна!</b>\n\n"
                f"💰 Получено: <b>{total_coins}</b> монет\n"
                f"{'🎁 Включая бонус: +' + str(bonus) if bonus > 0 else ''}\n\n"
                f"✨ Спасибо за покупку!"
            )

        else:  # gems
            package = GameConfig.GEM_PACKAGES[package_index]

            await db.add_gems(message.from_user.id, package['gems'])
            await db.add_transaction(
                message.from_user.id,
                'purchase',
                payment.total_amount,
                'stars',
                f"Куплено {package['gems']} гемов"
            )

            await message.answer(
                f"🎉 <b>Покупка успешна!</b>\n\n"
                f"💎 Получено: <b>{package['gems']}</b> гемов\n\n"
                f"✨ Спасибо за покупку!"
            )

    except Exception as e:
        await message.answer(
            f"❌ Ошибка обработки платежа. Обратитесь к администратору.\n"
            f"ID транзакции: {payment.telegram_payment_charge_id}"
        )
