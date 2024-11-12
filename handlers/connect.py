from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from database import get_user, activate_user, unfreeze_subscription
from aiogram.types.input_file import FSInputFile

video = FSInputFile("video.mp4")

router = Router()


@router.callback_query(F.data == "connect")
async def handle_devices(callback_query: CallbackQuery):
    # Удаление предыдущего сообщения
    await callback_query.message.delete()

    # Отображаем выбор устройства
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="iOS", callback_data="device_ios")],
            [InlineKeyboardButton(text="Android", callback_data="device_android")],
            [InlineKeyboardButton(text="Windows", callback_data="device_windows")],
            [InlineKeyboardButton(text="macOS", callback_data="device_macos")],
            [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
        ]
    )
    await callback_query.message.answer_video(video, caption="Выберите устройство", reply_markup=keyboard)


@router.callback_query(F.data.startswith("device_"))
async def process_device_selection(callback_query: CallbackQuery):
    await callback_query.message.delete()
    user_id = callback_query.from_user.id

    user = get_user(user_id)
    if user:
        days_remaining = user[1]
    else:
        days_remaining = 0

    if days_remaining <= 0:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Подписка", callback_data="subscription")],
                [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
            ]
        )
        await callback_query.message.answer_video(video, caption="Необходима подписка", reply_markup=keyboard)
        return

    device_type = callback_query.data.split('_')[1]

    vless = "vless://9265a2e3-8b32-490a-9e9a-13b148ee9a6f@188.225.81.134:433?type=tcp&security=reality&pbk=i2mCKTer5iNlnQnUxE9esSjpx2AZsvwOi8jYudePTjw&fp=chrome&sni=yahoo.com&sid=41c8eea9755212aa&spx=%2F&flow=xtls-rprx-vision#settstest-7dl2eiu4a"

    if device_type == "ios":
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Приложение", url="https://apps.apple.com/ru/app/v2box-v2ray-client/id6446814690")],
                [InlineKeyboardButton(text="Подключить", callback_data="get_vless")],
                [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
            ]
        )
        await callback_query.message.answer_video(video, caption='VPN активирован! Осталось 2 шага:\n\n1️⃣Скачайте и установите приложение перейдя по кнопке\n🌐Приложение👇\n\n2️⃣Нажмите на кнопку\n🏎Подключить👇',
                                            parse_mode="HTML",
                                            reply_markup=keyboard)
    elif device_type == "android":
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Приложение",
                                      url="https://play.google.com/store/apps/details?id=com.v2ray.ang&hl=ru")],
                [InlineKeyboardButton(text="Подключить", callback_data="get_vless")],
                [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
            ]
        )
        await callback_query.message.answer_video(video, caption='VPN активирован! Осталось 2 шага:\n\n1️⃣Скачайте и установите приложение перейдя по кнопке\n🌐Приложение👇\n\n2️⃣Нажмите на кнопку\n🏎Подключить👇\n\n3️⃣Далее в приложение, нажмите на три точки справа сверху, затем "Обновить подписку группы"',
                                            parse_mode="HTML",
                                            reply_markup=keyboard)
    elif device_type == "windows":
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Приложение",
                                      url="https://en.nekoray.org")],
                [InlineKeyboardButton(text="Подключить", callback_data="get_vless")],
                [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
            ]
        )
        await callback_query.message.answer_video(video, caption='VPN активирован! Осталось 2 шага:\n\n1️⃣Скачайте и установите приложение перейдя по кнопке\n🌐Приложение👇\n\n2️⃣Нажмите на кнопку\n🏎Подключить👇\n\n3️⃣Нажмите "Новый профиль", затем "Добавить профиль из буфера обмена" и нажмите "HI"',
                                            parse_mode="HTML",
                                            reply_markup=keyboard)
    elif device_type == "macos":
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Приложение",
                                      url="https://apps.apple.com/ru/app/v2box-v2ray-client/id6446814690")],
                [InlineKeyboardButton(text="Подключить", callback_data="get_vless")],
                [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
            ]
        )
        await callback_query.message.answer_video(video, caption='VPN активирован! Осталось 2 шага:\n\n1️⃣Скачайте и установите приложение перейдя по кнопке\n🌐Приложение👇\n\n2️⃣Нажмите на кнопку\n🏎Подключить👇',
                                            parse_mode="HTML",
                                            reply_markup=keyboard)
    activate_user(user_id)


@router.callback_query(F.data == "get_vless")
async def get_vless(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    unfreeze_subscription(user_id)
    vless = "vless://9265a2e3-8b32-490a-9e9a-13b148ee9a6f@188.225.81.134:433?type=tcp&security=reality&pbk=i2mCKTer5iNlnQnUxE9esSjpx2AZsvwOi8jYudePTjw&fp=chrome&sni=yahoo.com&sid=41c8eea9755212aa&spx=%2F&flow=xtls-rprx-vision#settstest-7dl2eiu4a"
    await callback_query.message.answer_video(video, caption="<code>{vless}</code>", parse_mode="HTML")
