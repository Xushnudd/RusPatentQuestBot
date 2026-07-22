from imp import *

info_router = Router()

@info_router.message(F.text == text_uz["main_menu"]["info"])
async def info(m: Message):
    reply = "".join(text_uz["info_text"])
    await m.answer(reply, parse_mode="Markdown")