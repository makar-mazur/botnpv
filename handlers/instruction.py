from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram import Router, F
from database import get_instruction
from aiogram.filters import Command
from aiogram.types.input_file import FSInputFile

video = FSInputFile("video.mp4")

router = Router()


@router.callback_query(F.data == "instruction")
async def show_instruction_menu(callback_query: CallbackQuery):
    await callback_query.message.delete()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1", callback_data="instruction_page_1"),
                InlineKeyboardButton(text="2", callback_data="instruction_page_2"),
                InlineKeyboardButton(text="3", callback_data="instruction_page_3")
            ],
            [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
        ]
    )

    await callback_query.message.answer_video(video, caption="1️⃣Базовая информация\n\n2️⃣Реферальная система\n\n3️⃣Пополнение средств",
                                        reply_markup=keyboard)


@router.callback_query(F.data.startswith("instruction_page_"))
async def show_instruction_page(callback_query: CallbackQuery):
    # await callback_query.message.delete()

    page = int(callback_query.data.split("_")[-1])
    text = get_instruction(page)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1", callback_data="instruction_page_1"),
                InlineKeyboardButton(text="2", callback_data="instruction_page_2"),
                InlineKeyboardButton(text="3", callback_data="instruction_page_3")
            ],
            [InlineKeyboardButton(text="Назад", callback_data="instruction")]
        ]
    )
    await callback_query.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == "instruction_back")
async def instruction_back(callback_query: CallbackQuery):
    await callback_query.message.edit_text("Возвращаемся в меню.", reply_markup=None)
