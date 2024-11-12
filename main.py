from loader import dp, bot
from handlers import setup_routers
import asyncio
from database import init_db


async def on_startup():
    init_db()
    print("Бот запущен")


async def main():
    # Регистрация всех хендлеров автоматически через setup_routers
    setup_routers(dp)

    await on_startup()

    # Запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
