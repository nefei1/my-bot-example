import os
import traceback 
from loguru import logger

from aiogram.types import ErrorEvent
from aiogram import Router

from src.db.models import User

router = Router()

@router.error()
async def error_handler(event: ErrorEvent, event_from_user, event_chat):
    exc = event.exception

    tb = traceback.extract_tb(exc.__traceback__)

    root = os.getcwd()
    
    user_frames = [frame for frame in tb if 'site-packages' not in frame.filename]
    
    if user_frames:
        last_frame = user_frames[-1]
    else:
        last_frame = tb[-1]

    func = last_frame.name
    line = last_frame.lineno
    code_line = last_frame.line

    if not event_chat:
        title = event_from_user.first_name
        chat_id = event_from_user.uid
        chat_type = "Private"
    else:
        title = event_chat.title
        chat_id = event_chat.chat_id
        chat_type = "Group"

    filename = os.path.relpath(last_frame.filename, start=root)

    logger.error(f"👤 User:\n   ├ 🆔 ID: {event_from_user.uid}\n   ├ 📛 Name: {event_from_user.first_name}\n   └ 📝 Username: {event_from_user or '\u2014'}\n\n💬 Chat:\n   ├ 🆔 ID: {chat_id}\n   ├ 🏷️ Title: {title}\n   └ 💡 Type: {chat_type}\n\n📁 File: {filename}\n🔧 Func: {func}\n📍 Line: {line}\n🧾 Code: {code_line}\n\n❌ Exc: {type(exc).__name__}: {exc}")