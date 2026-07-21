from lang.lang import text_uz
from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def startButton():
    builder = ReplyKeyboardBuilder()
    buttons = ["start_test", "my_results", "info"]
    
    for button in buttons:
        builder.add(KeyboardButton(text=f"{text_uz["main_menu"][button]}"))
    
    builder.adjust(2)
    result = builder.as_markup(resize_keyboard=True)
    
    return result