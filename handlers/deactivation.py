from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user, deactivate_user, freeze_subscription
from aiogram.types.input_file import FSInputFile

video = FSInputFile("video.mp4")

router = Router()


@router.callback_query(F.data == "deactivation")
async def deactivation_handler(callback_query: CallbackQuery):
    await callback_query.message.delete()
    user_id = callback_query.from_user.id

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
        ]
    )

    if get_user(user_id)[2]:
        deactivate_user(user_id)
        freeze_subscription(user_id)
        await callback_query.message.answer_video(video, caption="VPN деактивирован", reply_markup=keyboard)
    else:
        await callback_query.message.answer_video(video, caption="У вас нет активных устройств", reply_markup=keyboard)
