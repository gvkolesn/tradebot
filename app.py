from loader import db
from utils.set_bot_commands import set_default_commands


async def on_startup(dp):
    await db.create()

    import filters
    import middlewares
    filters.setup(dp)
    middlewares.setup(dp)

    from utils.notify_admins import on_startup_notify
    print("Создаем таблицу пользователей")
    await db.create_table_users()
    print("Готово")

    print("Создаем таблицу товаров")
    await db.create_table_goods()
    print("Готово")
    await on_startup_notify(dp)
    await set_default_commands(dp)


if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
