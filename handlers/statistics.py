from imp import *
import db.crud as db

statistics_router = Router()

@statistics_router.message(F.text == text_uz["main_menu"]["my_results"])
async def statistics(m: Message):
    from_id = str(m.from_user.id)
    first_name = m.from_user.first_name
    last_name = m.from_user.last_name or ""
    fullname = f"{first_name} {last_name}"
    
    user = await db.get_or_create_user(from_id)
    reply = (
        "📊 Sizning statistikangiz:\n\n"
        f"👤 *Ism:* {fullname}\n"
        f"🔢 *Yechilgan savollar*: {user.current_question_index}\n"
        f"⭐ *Status:* {'Premium' if user.is_premium else 'Bepul'}\n"
    )
    await m.answer(reply, parse_mode="Markdown")