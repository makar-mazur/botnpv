from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from database import add_subscription, get_total_user_ids
from loader import bot

router = Router()


class GiftState(StatesGroup):
    waiting_for_text = State()
    waiting_for_days = State()
    confirmation = State()


@router.message(Command("present"))
async def start_gift_process(message: Message, state: FSMContext):
    await message.answer("Для начала формирования подарка введите текст поздравления")
    await state.set_state(GiftState.waiting_for_text)


@router.message(GiftState.waiting_for_text)
async def input_gift_text(message: Message, state: FSMContext):
    await state.update_data(gift_text=message.text)
    await message.answer("Введите количество дней")
    await state.set_state(GiftState.waiting_for_days)


@router.message(GiftState.waiting_for_days)
async def input_gift_days(message: Message, state: FSMContext):
    try:
        days = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное количество дней (число).")
        return

    await state.update_data(gift_days=days)
    data = await state.get_data()
    gift_text = data['gift_text']

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отправить подарок", callback_data="send_gift")],
            [InlineKeyboardButton(text="Отменить", callback_data="cancel_gift")]
        ]
    )

    await message.answer(
        f"{gift_text}\n\nВы хотите отправить этот подарок на {days} дней?", reply_markup=keyboard
    )
    await state.set_state(GiftState.confirmation)


@router.callback_query(F.data == "send_gift", GiftState.confirmation)
async def send_gift(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()

    data = await state.get_data()
    gift_text = data.get('gift_text')
    gift_days = data.get('gift_days')

    user_ids = get_total_user_ids()
    user_ids = [user_id[0] for user_id in user_ids]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ЗАБРАТЬ ПОДАРОК", callback_data=f"get_gift_{gift_days}")]
        ]
    )

    for user_id in user_ids:
        try:
            await bot.send_message(user_id, gift_text, reply_markup=keyboard)
        except Exception as e:
            print(f"Ошибка при отправке пользователю {user_id}: {e}")

    await callback_query.message.answer("Подарок отправлен!")
    await state.clear()


@router.callback_query(F.data == "cancel_gift", GiftState.confirmation)
async def cancel_gift(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Операция отменена.")
    await state.clear()


@router.callback_query(F.data.startswith("get_gift_"))
async def cancel_gift(callback_query: CallbackQuery):
    await callback_query.message.delete()

    user_id = callback_query.from_user.id

    days_to_add = int(callback_query.data.split("_")[2])
    add_subscription(user_id, days_to_add)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
        ]
    )

    await callback_query.message.answer("Поздравляем! На ваш баланс зачислено 10 бонусных дней", reply_markup=keyboard)
