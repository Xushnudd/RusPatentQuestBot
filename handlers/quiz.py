from imp import *

quiz_router = Router()

@quiz_router.message(F.text == f"{text_uz["main_menu"]["start_test"]}")
async def start_test(m: Message):
    await m.answer("boshlandi")