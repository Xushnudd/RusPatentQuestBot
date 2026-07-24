import os
from dotenv import load_dotenv

from db.db import init_db

from fastapi import FastAPI, Request

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Update

from handlers.start import start_router
from handlers.quiz import quiz_router
from handlers.statistics import statistics_router
from handlers.info import info_router
from handlers.admin_handler import admin_router

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = FastAPI()
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(quiz_router)
dp.include_router(statistics_router)
dp.include_router(info_router)
dp.include_router(admin_router)
    
@app.post("/bots/ruspatentquest")
async def webhook(request: Request):
    await init_db()
    data = await request.json()
    update = Update(**data)
    
    await dp.feed_update(bot, update)
    return {"ok": True}