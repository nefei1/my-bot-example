from aiogram import Router

from .basic import *
from .error import *

router = Router()

def get_routers() -> Router:
    
    router.include_routers(
        basic.router,
        error.router
    )
    return router