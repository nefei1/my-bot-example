from aiogram import Router
from .basic import *

router = Router()

def get_routers() -> Router:
    
    router.include_routers(
        basic.router
    )
    return router