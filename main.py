import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from db.db import init_db

from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update

from handlers.start import start_router
from handlers.quiz import quiz_router
from handlers.statistics import statistics_router
from handlers.info import info_router
from handlers.admin_handler import admin_router

from db.seed import main

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(quiz_router)
dp.include_router(statistics_router)
dp.include_router(info_router)
dp.include_router(admin_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    if WEBHOOK_URL:
        await bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
        await main()
    
    yield
    
    await bot.delete_webhook()
    await bot.session.close()


app = FastAPI(lifespan=lifespan)


@app.post("/bots/ruspatentquest")
async def webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data, context={"bot": bot})
    
    await dp.feed_update(bot, update)
    return {"ok": True}