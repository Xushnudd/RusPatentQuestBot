import os
from dotenv import load_dotenv

import asyncio
from aiogram import Bot, Dispatcher

from handlers.start import start_router

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

async def main():
    dp.include_router(start_router)

    await dp.start_polling(bot)

asyncio.run(main())