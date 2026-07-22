import os
import logging
from dotenv import load_dotenv

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db.crud import update_user

# .env faylini yuklaymiz
load_dotenv()

# ENV'dan admin ID-sini olamiz
ADMIN_ID = os.getenv("IS_ADMIN")

admin_router = Router()


class AdminStates(StatesGroup):
    waiting_for_forward = State()


@admin_router.message(Command("admin"))
async def admin_panel_start(message: Message, state: FSMContext):
    # Faqat .env dagi adminga ruxsat beramiz
    if str(message.from_user.id) != str(ADMIN_ID):
        await message.answer("❌ Sizga ushbu bo'limdan foydalanishga ruxsat berilmagan.")
        return

    await state.set_state(AdminStates.waiting_for_forward)
    await message.answer(
        "👨‍💻 <b>Admin panelga xush kelibsiz!</b>\n\n"
        "Premium bermoqchi bo'lgan foydalanuvchingizning istalgan xabarini ushbu chatga <b>forward</b> (qayta yo'naltirib) qiling.",
        parse_mode="HTML"
    )


@admin_router.message(AdminStates.waiting_for_forward)
async def process_forwarded_message(message: Message, state: FSMContext):
    # Admin haqiqatan ham xabarni forward qilganini / boshqa odam emasligini tekshiramiz
    if str(message.from_user.id) != str(ADMIN_ID):
        return

    # Forward qilingan xabardan user_id olish
    target_user_id = None

    if message.forward_from:
        target_user_id = str(message.forward_from.id)
    elif message.forward_from_chat:
        # Agar kanal yoki guruhdan forward qilingan bo'lsa
        target_user_id = str(message.forward_from_chat.id)

    # Agar foydalanuvchi o'z maxfiylik sozlamalarida (privacy settings)
    # forward xabarlarga havola qo'yishni taqiqlab qo'ygan bo'lsa:
    if not target_user_id:
        await message.answer(
            "⚠️ Ushbu foydalanuvchi o'z hisobida <b>Maxfiylik sozlamalari</b>ni (Forwarded Messages Privacy) yoqib qo'ygani sababli uning ID-sini olib bo'lmadi.\n\n"
            "Iltimos, boshqa xabarini forward qiling yoki foydalanuvchiga sozlamasini vaqtincha o'chirishni ayting.",
            parse_mode="HTML"
        )
        return

    try:
        # Bazada is_premium funksiyasini True ga o'zgartiramiz
        await update_user(user_id=target_user_id, field_name="is_premium", new_data=True)

        # Adminga tasdiq xabari
        user_name = message.forward_from.full_name if message.forward_from else "Foydalanuvchi"
        await message.answer(
            f"✅ <b>Muvaffaqiyatli bajarildi!</b>\n\n"
            f"👤 Foydalanuvchi: <b>{user_name}</b>\n"
            f"🆔 ID: <code>{target_user_id}</code>\n"
            f"💎 Premium maqomi aktivlashtirildi!",
            parse_mode="HTML"
        )

        # Foydalanuvchiga ham xabar yuborish (ixtiyoriy)
        try:
            await message.bot.send_message(
                chat_id=target_user_id,
                text="🎉 <b>Xushxabar!</b> Sizga botda <b>Premium</b> maqomi berildi. Endi cheklovlarsiz test ishlashingiz mumkin!",
                parse_mode="HTML"
            )
        except Exception as e:
            logging.warning(f"Foydalanuvchiga xabar yuborishda xatolik (botni bloklagan bo'lishi mumkin): {e}")

    except Exception as e:
        logging.error(f"Bazada user ma'lumotini yangilashda xatolik: {e}")
        await message.answer(f"❌ Xatolik yuz berdi: {e}")

    # Holatni toizalaymiz
    await state.clear()