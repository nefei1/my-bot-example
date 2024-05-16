from contextlib import suppress

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram_i18n import I18nContext

from src.db import Database, User
from src.keyboards import lang_markup

router = Router()

@router.message(Command('start'))
async def start_cmd(m: Message, i18n: I18nContext, user: User):
    uid = m.from_user.id
    first_name = m.from_user.first_name

    if not user.choosen_language:
        markup = lang_markup(uid)

        await m.answer(text=i18n.get("choose_lang"), reply_markup=markup) 
    else:
        await m.answer(text=i18n.get("hello", first_name=first_name))

@router.message(Command('lang'))
async def language_cmd(m: Message, i18n: I18nContext):
    uid = m.from_user.id

    markup = lang_markup(uid)

    await m.answer(text=i18n.get("choose_lang"), reply_markup=markup) 


@router.callback_query(F.data.startswith("choose_lang:"))
async def choose_lang_callback(call: CallbackQuery, i18n: I18nContext, user: User, db: Database):
    lang = call.data.split(":")[1]

    uid = call.from_user.id

    choosen_language = user.choosen_language
    await i18n.set_locale(lang)
    if not choosen_language:
        user.choosen_language = True
    await db.commit()

    markup = lang_markup(uid)

    with suppress(TelegramBadRequest):
        await call.message.edit_text(i18n.get("choose_lang"), reply_markup=markup)
    if not choosen_language:
        await call.message.answer(i18n.get("hello", first_name=call.from_user.first_name))
    await call.answer(i18n.get("choosen_lang", lang=lang))