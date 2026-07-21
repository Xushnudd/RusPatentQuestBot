from lang.lang import text_uz
from keyboards.keyboards import startButton

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

start_router = Router()

@start_router.message(CommandStart())
async def start(m: Message):
    first_name = m.from_user.first_name
    last_name = m.from_user.last_name if None else ""
    fullname = f"{first_name} {last_name}"
    reply = (
        f"{text_uz["welcome_message"]}".format(fullname=fullname)
    )
    await m.answer(reply, parse_mode="Markdown", reply_markup=startButton())