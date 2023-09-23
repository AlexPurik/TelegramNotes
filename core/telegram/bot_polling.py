from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from .bot_instance import bot
from .handlers import r1, r2, r3


dp = Dispatcher(storage=MemoryStorage())


async def start_bot():
    dp.include_router(r1)
    dp.include_router(r2)
    dp.include_router(r3)

    print("Bot started!")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def stop_bot():
    await bot.close()
    await dp.storage.close()
    print("Bot stopped!")
