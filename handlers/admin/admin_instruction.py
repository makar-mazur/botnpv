from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from database import update_instruction

router = Router()


class InstructionEditStates(StatesGroup):
    waiting_for_page = State()
    waiting_for_text = State()
    waiting_for_confirmation = State()


@router.message(Command('instruction'))
async def start_instruction_edit(message: Message, state: FSMContext):
    await message.answer("Отправьте цифру раздела инструкции (1, 2 или 3):")
    await state.set_state(InstructionEditStates.waiting_for_page)


@router.message(InstructionEditStates.waiting_for_page)
async def instruction_page_selected(message: Message, state: FSMContext):
    page = message.text.strip()
    if page not in ["1", "2", "3"]:
        await message.answer("Пожалуйста, введите корректный номер раздела (1, 2 или 3):")
        return

    await state.update_data(page=int(page))
    await message.answer("Отправьте текст для этого раздела:")
    await state.set_state(InstructionEditStates.waiting_for_text)


@router.message(InstructionEditStates.waiting_for_text)
async def instruction_text_entered(message: Message, state: FSMContext):
    new_text = message.text
    await state.update_data(new_text=new_text)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Сохранить", callback_data="save_instruction")],
            [InlineKeyboardButton(text="Отменить", callback_data="cancel_instruction")]
        ]
    )
    await message.answer(f"Вы ввели следующий текст:\n\n{new_text}\n\nСохранить изменения?", reply_markup=keyboard)
    await state.set_state(InstructionEditStates.waiting_for_confirmation)


@router.callback_query(F.data == "save_instruction")
async def save_instruction(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    page = data['page']
    new_text = data['new_text']
    update_instruction(page, new_text)

    await callback_query.message.edit_text(f"Текст инструкции для раздела {page} обновлен.")
    await state.clear()


@router.callback_query(F.data == "cancel_instruction")
async def cancel_instruction(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Операция отменена.")
    await state.clear()
