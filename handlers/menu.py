from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user, get_time_until_subscription_end
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile

video = FSInputFile("video.mp4")

router = Router()


async def send_menu(user_id, message):
    # Получаем информацию о пользователе
    user = get_user(user_id)

    if user:
        days_remaining = user[4]  # Получаем количество оставшихся дней подписки
    else:
        days_remaining = 0  # Если пользователя нет в базе, по умолчанию 0 дней

    # Отображаем меню с информацией о подписке
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подписка", callback_data="subscription")],
            [InlineKeyboardButton(text="Подключить", callback_data="connect")],
            [InlineKeyboardButton(text="Деактивация", callback_data="deactivation")],
            [InlineKeyboardButton(text="Инструкция", callback_data="instruction")],
            [InlineKeyboardButton(text="Поделиться", switch_inline_query=f"https://t.me/mytestcodebotbot?start={user_id}")]
        ]
    )

    user_sub = get_time_until_subscription_end(user_id)
    if user_sub == False:
        user_sub = "Нет"

    # Выводим информацию как на схеме
    await message.answer_video(video, caption=f"Kedo - ваш премиум VPN\n\nВаша подписка: {user_sub}\n\nПоддержка: @kedoaskbot", reply_markup=keyboard)


# Обработчик кнопки "Назад" для возврата в меню
@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.delete()
    user_id = callback_query.from_user.id

    await send_menu(user_id, callback_query.message)
    await callback_query.answer()
