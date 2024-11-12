from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from database import get_total_users, get_active_users, get_inactive_users, get_total_payments, get_total_campaigns, get_used_promo_code_count

router = Router()


@router.message(Command("stats"))
async def stats_handler(message: Message):
    total_users = get_total_users()
    total_payments = get_total_payments()
    active_users = get_active_users()
    inactive_users = get_inactive_users()
    left_users = 0
    shares = 0
    entered_promos = get_used_promo_code_count()
    campaigns = get_total_campaigns()
    await message.reply(f"Всего пополнено: {total_payments} RUB\nВсего пользователей: "
                        f"{total_users}\nПользователей активно: {active_users}\nПользователей неактивно: {inactive_users}"
                        f"\nУшедших пользователей: {left_users}\nСколько поделились: {shares}\nВведено промокодов: "
                        f"{entered_promos}\nРекламных кампаний: {campaigns}")


@router.callback_query(Command("newcamp"))
async def handle_campaigns(callback_query: CallbackQuery):
    # Удаление предыдущего сообщения
    await callback_query.message.delete()

    await callback_query.message.answer("Здесь будет управление рекламными кампаниями.")


@router.callback_query(Command("instruction"))
async def handle_broadcast(callback_query: CallbackQuery):
    await callback_query.message.delete()

    await callback_query.message.answer("Здесь будет управление инструкцией.")


@router.callback_query(Command("message"))
async def handle_broadcast(callback_query: CallbackQuery):
    # Удаление предыдущего сообщения
    await callback_query.message.delete()

    await callback_query.message.answer("Здесь будет отправка сообщений.")


@router.callback_query(Command("present"))
async def handle_broadcast(callback_query: CallbackQuery):
    # Удаление предыдущего сообщения
    await callback_query.message.delete()

    await callback_query.message.answer("Здесь будут подарки.")
