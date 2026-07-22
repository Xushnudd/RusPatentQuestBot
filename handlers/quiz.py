import random
import logging
import asyncio
import aiohttp
from deep_translator import GoogleTranslator
from imp import *
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from aiogram.fsm.context import FSMContext

from db.crud import get_quest, get_random_quests, get_or_create_user, update_user

quiz_router = Router()
translator = GoogleTranslator(source='ru', target='uz')

async def check_user_progress(user_id: str, admin_username: str, bot) -> bool:
    user = await get_or_create_user(user_id)
    correct_answers = user.current_question_index 
    
    if correct_answers >= 10 and not user.is_premium:
        message = (
            f"Siz 10 ta to'g'ri javob berdingiz! 🎯\n"
            f"Testni davom ettirish uchun premium sotib olishingiz kerak.\n\n"
            f"Murojaat uchun: @{admin_username}"
        )
        await bot.send_message(user_id, message)
        return False
        
    return True

async def translate_text(text: str) -> str:
    """Matnni o'zbek tiliga asinxron tarjima qilish"""
    if not text:
        return ""
    try:
        return await asyncio.to_thread(translator.translate, text)
    except Exception as e:
        logging.error(f"Tarjima qilishda xatolik: {e}")
        return text

def prepare_question_keyboard(options_count: int, correct_index: int, shuffled_indices: list) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for display_num, original_idx in enumerate(shuffled_indices, start=1):
        cb_data = f"ans_{original_idx}_{correct_index}"
        row.append(InlineKeyboardButton(text=str(display_num), callback_data=cb_data))
    
    buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@quiz_router.message(F.text == text_uz["main_menu"]["start_test"])
async def start_quiz(m: Message, state: FSMContext):
    from_id = str(m.from_user.id)
    
    can_continue = await check_user_progress(from_id, admin_username="Blaskn1", bot=m.bot)
    if not can_continue:
        return

    quest_ids = await get_random_quests()
    if not quest_ids:
        await m.answer("⚠️ Bazada hali savollar yo'q!")
        return

    await state.update_data(
        quest_ids=quest_ids,
        quest_index=0,
        sub_question_index=0,
        correct_count=0,
        total_answered=0
    )
    await send_current_question(m, state)


async def send_audio_from_url(bot, chat_id: int, url: str, caption: str, reply_markup: InlineKeyboardMarkup) -> bool:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    audio_bytes = await response.read()
                    filename = url.split("/")[-1] or "audio.mp3"
                    audio_file = BufferedInputFile(audio_bytes, filename=filename)
                    
                    await bot.send_audio(
                        chat_id=chat_id,
                        audio=audio_file,
                        caption=caption,
                        reply_markup=reply_markup,
                        parse_mode="HTML"
                    )
                    return True
                else:
                    logging.error(f"Audio server HTTP status: {response.status}")
    except Exception as e:
        logging.error(f"Audio yuklab yuborishda xatolik: {e}")
    
    return False


# 2. Savolni yuborish funksiyasi
async def send_current_question(event: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quest_ids = data.get("quest_ids", [])
    q_idx = data.get("quest_index", 0)
    sub_q_idx = data.get("sub_question_index", 0)

    if q_idx >= len(quest_ids):
        total = data.get("total_answered", 0)
        correct = data.get("correct_count", 0)
        
        result_text = (
            f"🎉 <b>Test yakunlandi! / Тест завершен!</b>\n\n"
            f"📊 Jami javob berilgan savollar: <b>{total}</b> ta\n"
            f"✅ To'g'ri javoblar: <b>{correct}</b> ta\n"
            f"❌ Noto'g'ri javoblar: <b>{total - correct}</b> ta"
        )
        
        if isinstance(event, CallbackQuery):
            await event.message.answer(result_text, parse_mode="HTML")
        else:
            await event.answer(result_text, parse_mode="HTML")
            
        await state.clear()
        return

    current_quest = await get_quest(quest_ids[q_idx])
    
    if not current_quest or not getattr(current_quest, "questions", None):
        await state.update_data(quest_index=q_idx + 1, sub_question_index=0)
        await send_current_question(event, state)
        return

    questions_list = current_quest.questions
    
    if sub_q_idx >= len(questions_list):
        await state.update_data(quest_index=q_idx + 1, sub_question_index=0)
        await send_current_question(event, state)
        return

    sub_q = questions_list[sub_q_idx]
    correct_idx = sub_q.get("correct", 0)
    options = sub_q.get("options") or []
    if not options:
        await state.update_data(sub_question_index=sub_q_idx + 1)
        await send_current_question(event, state)
        return

    shuffled_indices = list(range(len(options)))
    random.shuffle(shuffled_indices)

    ru_assignment = getattr(current_quest, "assignment", None)
    ru_question = sub_q['question']

    # 1. Assignment va Question bir xil bo'lsa, ikkinchi marta ko'rsatmaymiz
    show_assignment = ru_assignment and ru_assignment.strip() != ru_question.strip()
    uz_assignment = await translate_text(ru_assignment) if show_assignment else ""
    uz_question = await translate_text(ru_question)

    # 2. Ruscha variantlarni tayyorlash
    ru_opts = [options[i] for i in shuffled_indices]

    # 3. BARCHA VARIANTLARNI BITTA SO'ROVDA TARJIMA QILAMIZ (Google IP block bermaydi va to'g'ri tarjima qiladi)
    combined_ru_opts = "\n".join(ru_opts)
    combined_uz_opts = await translate_text(combined_ru_opts)
    uz_opts = combined_uz_opts.split("\n")

    # 4. Ruscha matnni yig'ish
    ru_text = f"📋 <b>{ru_assignment}</b>\n\n" if show_assignment else ""
    ru_text += f"❓ <b>{ru_question}</b>\n\n"
    for num, opt in enumerate(ru_opts, start=1):
        ru_text += f"<b>{num}.</b> {opt}\n"

    # 5. O'zbekcha matnni yig'ish
    uz_text = f"📋 <b>{uz_assignment}</b>\n\n" if show_assignment else ""
    uz_text += f"❓ <b>{uz_question}</b>\n\n"

    # Agar tarjima bo'lingan qatorlar soni mos tushsa uz_opts, aks holda ru_opts ishlatamiz
    display_uz_opts = uz_opts if len(uz_opts) == len(ru_opts) else ru_opts
    for num, opt in enumerate(display_uz_opts, start=1):
        uz_text += f"<b>{num}.</b> {opt}\n"

    caption_text = f"{ru_text}\n------------\n\n{uz_text}"
    kb = prepare_question_keyboard(len(options), correct_idx, shuffled_indices)

    chat_id = event.message.chat.id if isinstance(event, CallbackQuery) else event.chat.id
    bot = event.bot

    if getattr(current_quest, "audio", None) and sub_q_idx == 0:
        audio_val = current_quest.audio.strip().lstrip("/")
        audio_url = audio_val if audio_val.startswith("http") else f"https://testpatent.ru/audio/{audio_val}"

        sent_success = await send_audio_from_url(bot, chat_id, audio_url, caption_text, kb)

        if not sent_success:
            await bot.send_message(
                chat_id=chat_id,
                text=caption_text,
                reply_markup=kb,
                parse_mode="HTML"
            )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text=caption_text,
            reply_markup=kb,
            parse_mode="HTML"
        )


@quiz_router.callback_query(F.data.startswith("ans_"))
async def handle_answer(call: CallbackQuery, state: FSMContext):
    _, chosen_str, correct_str = call.data.split("_")
    chosen_idx = int(chosen_str)
    correct_idx = int(correct_str)
    
    user_id = str(call.from_user.id)
    data = await state.get_data()
    correct_count = data.get("correct_count", 0)
    total_answered = data.get("total_answered", 0)
    sub_q_idx = data.get("sub_question_index", 0)

    # Eski knopkalarni olib tashlaymiz
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    if chosen_idx == correct_idx:
        correct_count += 1
        await call.answer("✅ To'g'ri javob!", show_alert=False)
        
        user = await get_or_create_user(user_id)
        new_index = user.current_question_index + 1
        await update_user(user_id, "current_question_index", new_index)

        can_continue = await check_user_progress(user_id, admin_username="Blaskn1", bot=call.bot)
        if not can_continue:
            await state.clear()
            return
    else:
        await call.answer("❌ Noto'g'ri javob!", show_alert=False)

    await state.update_data(
        sub_question_index=sub_q_idx + 1,
        correct_count=correct_count,
        total_answered=total_answered + 1
    )

    await send_current_question(call, state)