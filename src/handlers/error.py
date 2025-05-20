import traceback 
from loguru import logger

from aiogram.types import ErrorEvent
from aiogram import Router

router = Router()

@router.error()
async def error_handler(event: ErrorEvent):
    exc = event.exception

    tb = traceback.format_exc()
    
    logger.error(tb)