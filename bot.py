import os
from dotenv import load_dotenv

from db.db import init_db

import asyncio
from aiogram import Bot, Dispatcher

from handlers.start import start_router
from handlers.quiz import quiz_router
from handlers.statistics import statistics_router
from handlers.info import info_router

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

async def main():
    dp.include_router(start_router)
    dp.include_router(quiz_router)
    dp.include_router(statistics_router)
    dp.include_router(info_router)
    
    await init_db()
    await dp.start_polling(bot)

asyncio.run(main())