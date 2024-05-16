# from typing import 

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def inline_builder(*buttons: list[str], adjust: list[int] | int = None) -> InlineKeyboardMarkup:
    '''
    Builder for inline keyboard

    example: `inline_builder(["Hello", "world"])` -> `InlineKeyboardMarkup(InlineKeyboardButton(text="Hello", callback_data="world"))`
   
    '''

    builder = InlineKeyboardBuilder()
    for button in buttons:
        builder.add(InlineKeyboardButton(text=button[0], callback_data=button[1]))

    if adjust:
        builder.adjust(adjust)
    
    return builder.as_markup()
    
def lang_markup(uid: int) -> InlineKeyboardMarkup:
    return inline_builder(["🇺🇸 English", f"choose_lang:en:{uid}"], ["🇷🇺 Русский", f"choose_lang:ru:{uid}"])
