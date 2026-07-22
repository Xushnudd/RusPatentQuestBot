from os import getenv
from dotenv import load_dotenv
load_dotenv()
from imp import *
from keyboards.keyboards import startButton
from aiogram.filters import CommandStart
import db.crud as db

start_router = Router()
IS_ADMIN = getenv("IS_ADMIN")

@start_router.message(CommandStart())
async def start(m: Message):
    from_id = str(m.from_user.id)
    first_name = m.from_user.first_name
    last_name = m.from_user.last_name or ""
    fullname = f"{first_name} {last_name}"
    
    user = await db.get_or_create_user(from_id)
    
    reply = text_uz["welcome_message"].format(fullname=fullname)
    
    if str(user.user_id) == IS_ADMIN:
        if not user.is_admin:
            user = await db.update_user(from_id, "is_admin", True)
        reply+="\n\n*Admin panelga kirish uchun /admin ustiga bosing !*"
        
    await m.answer(reply, parse_mode="Markdown", reply_markup=startButton())