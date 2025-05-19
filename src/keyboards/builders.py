# from typing import 

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

    
def lang_markup(uid: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="🇺🇸 English", callback_data=f"choose_lang:en:{uid}"), InlineKeyboardButton(text="🇷🇺 Русский", callback_data=f"choose_lang:ru:{uid}"))

    return builder.as_markup()