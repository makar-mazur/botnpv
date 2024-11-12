from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from database import get_total_users, get_active_users, get_inactive_users, get_total_payments
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database import add_campaign

router = Router()


class CampaignStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_promo_code = State()
    waiting_for_bonus_days = State()
    waiting_for_referral_id = State()


@router.message(Command('newcamp'))
async def start_new_campaign(message: Message, state: FSMContext):
    await message.answer("Введите название кампании:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(CampaignStates.waiting_for_name)


@router.message(CampaignStates.waiting_for_name)
async def campaign_name_entered(message: Message, state: FSMContext):
    await state.update_data(name=message.md_text)
    await message.answer("Введите промокод кампании (только латинские буквы и цифры):")
    await state.set_state(CampaignStates.waiting_for_promo_code)


@router.message(CampaignStates.waiting_for_promo_code)
async def campaign_promo_code_entered(message: Message, state: FSMContext):
    promo_code = message.text
    if not promo_code.isalnum():
        await message.answer("Промокод должен состоять только из латинских букв и цифр. Попробуйте снова.")
        return
    await state.update_data(promo_code=promo_code)
    await message.answer("Введите количество дней для бонусного периода:")
    await state.set_state(CampaignStates.waiting_for_bonus_days)


@router.message(CampaignStates.waiting_for_bonus_days)
async def campaign_bonus_days_entered(message: Message, state: FSMContext):
    try:
        bonus_days = int(message.text)
        if bonus_days <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите корректное количество дней (целое положительное число):")
        return
    await state.update_data(bonus_days=bonus_days)
    await message.answer("Введите реферальный ID кампании:")
    await state.set_state(CampaignStates.waiting_for_referral_id)


@router.message(CampaignStates.waiting_for_referral_id)
async def campaign_referral_id_entered(message: Message, state: FSMContext):
    referral_id = message.text
    data = await state.get_data()
    name = data['name']
    promo_code = data['promo_code']
    bonus_days = data['bonus_days']

    # Вызов функции для добавления кампании
    add_campaign(name, promo_code, bonus_days, referral_id)

    await message.answer(f"Кампания '{name}' успешно создана!")
    await state.clear()
