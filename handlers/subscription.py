from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from handlers.payments import create, check
from database import add_payment, get_all_promo_codes, get_campaign_by_promo_code, add_subscription, add_used_promo_code_count, ban_promo, if_ban_promo, save_used_promo_code, promo_code_already_used
import time
import datetime
from aiogram.types.input_file import FSInputFile

video = FSInputFile("video.mp4")

router = Router()


class SubscriptionState(StatesGroup):
    waiting_for_payment = State()


class PromoCodeState(StatesGroup):
    waiting_for_promo_code = State()
    failed_attempts = State()


@router.callback_query(F.data == "subscription")
async def handle_subscription(callback_query: CallbackQuery):
    await callback_query.message.delete()

    user_id = callback_query.from_user.id

    if if_ban_promo(user_id):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="1 месяц", callback_data="sub_1_month"),
                    InlineKeyboardButton(text="3 месяца", callback_data="sub_3_months")
                ],
                [
                    InlineKeyboardButton(text="6 месяцев", callback_data="sub_6_months"),
                    InlineKeyboardButton(text="1 год", callback_data="sub_1_year")
                ],
                [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
            ]
        )
        await callback_query.message.answer_video(video, caption="Выберите срок подписки:", reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="1 месяц", callback_data="sub_1_month"),
                    InlineKeyboardButton(text="3 месяца", callback_data="sub_3_months")
                ],
                [
                    InlineKeyboardButton(text="6 месяцев", callback_data="sub_6_months"),
                    InlineKeyboardButton(text="1 год", callback_data="sub_1_year")
                ],
                [InlineKeyboardButton(text="Промокод", callback_data="promo_code")],
                [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
            ]
        )
        await callback_query.message.answer_video(video, caption="Выберите срок подписки:", reply_markup=keyboard)


@router.callback_query(F.data == "promo_code")
async def start_promo_code_input(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
        ]
    )
    await callback_query.message.answer_video(video, caption="Отправьте промокод и получите на баланс до 30 бонусных дней", reply_markup=keyboard)
    await state.set_state(PromoCodeState.waiting_for_promo_code)
    await state.update_data(attempts_left=3)


@router.message(PromoCodeState.waiting_for_promo_code)
async def process_promo_code(message: Message, state: FSMContext):
    promo_codes = get_all_promo_codes()

    user_input = message.text.strip()

    data = await state.get_data()
    attempts_left = data.get('attempts_left', 3)

    campaign = get_campaign_by_promo_code(user_input)
    user_id = message.from_user.id

    if promo_code_already_used(user_id, user_input):
        await message.answer("Вы уже использовали этот промокод.")
        return

    if user_input in promo_codes:
        bonus_days = campaign[4]
        add_subscription(user_id, bonus_days)
        add_used_promo_code_count()
        save_used_promo_code(user_id, user_input)

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="СПАСИБО", callback_data="back_to_menu")]
            ]
        )
        await message.answer_video(video, caption=f"Поздравляем! По промокоду Вам начислено {bonus_days} бонусных дней!", reply_markup=keyboard)
        await state.clear()
    else:
        attempts_left -= 1
        if attempts_left > 0:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
                ]
            )
            await message.answer_video(video, caption="Промокод не подошёл\nОсталось {attempts_left} попытки.", reply_markup=keyboard)
            await state.update_data(attempts_left=attempts_left)
        else:
            ban_promo(user_id)
            await message.answer_video(video, caption="Вы исчерпали все попытки. Кнопка 'Промокод' больше не будет доступна.")
            await state.clear()


@router.callback_query(F.data.startswith("sub_"))
async def show_profile_info(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()

    if callback_query.data == "sub_1_month":
        period = "1 месяц"
        amount = "300.00"
    elif callback_query.data == "sub_3_months":
        period = "3 месяца"
        amount = "900.00"
    elif callback_query.data == "sub_6_months":
        period = "6 месяцев"
        amount = "1800.00"
    elif callback_query.data == "sub_1_year":
        period = "1 год"
        amount = "3600.00"
    else:
        return

    await state.update_data(period=period, amount=amount)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Перейти к оплате", callback_data="pay")],
            [InlineKeyboardButton(text="Назад", callback_data="subscription")]
        ]
    )
    await callback_query.message.answer_video(video, caption="Вы выбрали подписку на {period}. Сумма к оплате: {amount} RUB.\n\nДля оплаты нажмите на кнопку ниже.", reply_markup=keyboard)


@router.callback_query(F.data == "pay")
async def process_payment(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()

    user_data = await state.get_data()
    amount = user_data['amount']
    period = user_data['period']

    # Создаем платеж
    confirmation_url, payment_id = create(amount, callback_query.from_user.id, period)

    await state.update_data(payment_id=payment_id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Перейти к оплате", url=confirmation_url)],
            [InlineKeyboardButton(text="Проверить оплату", callback_data="check_payment")]
        ]
    )
    await callback_query.message.answer_video(video, caption="Счёт для оплаты профиля на {period} сформирован.\nДля оплаты перейдите по ссылке ниже.", reply_markup=keyboard)


@router.callback_query(F.data == "check_payment")
async def check_handler(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    payment_id = user_data['payment_id']
    period = user_data['period']

    await callback.message.delete()

    result = check(payment_id)

    if result:
        user_id = callback.from_user.id
        if period == "1 месяц":
            amount = 300
            days_to_add = 30
        elif period == "3 месяца":
            amount = 900
            days_to_add = 90
        elif period == "6 месяцев":
            amount = 1800
            days_to_add = 180
        elif period == "1 год":
            amount = 3600
            days_to_add = 360
        else:
            days_to_add = 0

        add_subscription(user_id, days_to_add)
        add_payment(user_id, amount)

        await state.clear()

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="В меню", callback_data="back_to_menu")]
            ]
        )
        await callback.message.answer_video(video, caption='Оплата прошла успешно! Вам начислено {days_to_add} дней подписки.',
                                      reply_markup=keyboard)

    else:
        confirmation_url = callback.message.reply_markup.inline_keyboard[0][0].url
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Перейти к оплате", url=confirmation_url)],
                [InlineKeyboardButton(text="Проверить оплату", callback_data="check_payment")]
            ]
        )
        await callback.message.answer_video(video, caption='Оплата ещё не прошла или возникла ошибка.', reply_markup=keyboard)

    await callback.answer()
