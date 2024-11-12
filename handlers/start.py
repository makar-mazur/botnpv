from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.input_file import FSInputFile
from aiogram.filters import Command
from database import add_user, get_user, deactivate_user, add_subscription, user_exists, freeze_subscription, add_user_with_subscription
from loader import bot

router = Router()


@router.message(Command("start"))
async def start(message: Message):
    user_id = message.from_user.id

    video = FSInputFile("video.mp4")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Меню", callback_data="back_to_menu")]
        ]
    )
    keyboard_1 = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="СПАСИБО", callback_data="back_to_menu")]
        ]
    )

    if user_exists(user_id):
        await message.answer_video(video, caption="Добро пожаловать обратно!", reply_markup=keyboard)
    else:
        start_command = message.text
        referrer_id = str(start_command[7:])
        if str(referrer_id) != "":
            if str(referrer_id) != str(user_id):
                add_user_with_subscription(user_id, 5, referrer_id)
                try:
                    await bot.send_video(referrer_id, video, caption="Поздравляем! По реферальным вам начислено 15 бонусных дней!", reply_markup=keyboard_1)
                    add_subscription(referrer_id, 15)
                except:
                    pass
            else:
                await message.answer_video(video, caption="Нельзя регистрироваться по собственной реферальной ссылке!")
        else:
            add_user_with_subscription(user_id, 5)

        await message.answer_video(video, caption="Для начала работы с ботом Вам начислено 5 бонусных дней!", reply_markup=keyboard)
