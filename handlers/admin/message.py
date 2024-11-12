from aiogram import Router, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_total_user_ids
from loader import bot

router = Router()


class Form(StatesGroup):
    waiting_for_text = State()
    waiting_for_image = State()
    preview = State()


@router.message(Command("message"))
async def cmd_message(message: Message, state: FSMContext):
    await message.answer("Отправьте текст для рассылки")
    await state.set_state(Form.waiting_for_text)


@router.message(Form.waiting_for_text, F.text)
async def process_text(message: Message, state: FSMContext):
    await state.update_data(text=message.md_text)
    await message.answer("Отправьте картинку для рассылки")
    await state.set_state(Form.waiting_for_image)


@router.message(Form.waiting_for_image, F.photo)
async def process_image(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)

    data = await state.get_data()
    text = data.get('text')
    photo_file_id = data.get('photo')

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отправить", callback_data="send")],
            [InlineKeyboardButton(text="Отменить", callback_data="cancel")]
        ]
    )

    await message.answer_photo(photo_file_id, caption=text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN_V2)
    await state.set_state(Form.preview)


@router.callback_query(F.data == 'send', Form.preview)
async def send_broadcast(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get('text')
    photo_file_id = data.get('photo')

    user_ids = get_total_user_ids()
    user_ids = [user_id[0] for user_id in user_ids]

    for user_id in user_ids:
        try:
            await bot.send_photo(user_id, photo_file_id, caption=text, parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            print(f"Ошибка при отправке пользователю {user_id}: {e}")

    await callback_query.message.answer("Рассылка успешно отправлена!")
    await state.clear()


@router.callback_query(F.data == 'cancel', Form.preview)
async def cancel_broadcast(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Рассылка отменена.")
    await state.clear()
