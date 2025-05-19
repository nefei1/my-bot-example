from typing import Annotated
from contextlib import suppress

from aiogram.types import User as TgUser
from aiogram_i18n.managers import BaseManager

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BIGINT, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from .base import Base

#object for type of telegram ids
_id = Annotated[int, mapped_column(BIGINT)]

#object for primary keys
prid = Annotated[int, mapped_column(primary_key=True)]

class User(Base):
    __tablename__ = "User"

    #Unique telegram id
    uid: Mapped[_id]
    
    #first name of user
    first_name: Mapped[str]
    
    #language that used by i18n
    language: Mapped[str]

    choosen_language: Mapped[bool] = mapped_column(default=False)

    #primary key
    id: Mapped[prid]


class Database:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, telegram_user: TgUser, language: str):
        user = User(uid=telegram_user.id, first_name=telegram_user.first_name, language=language)
        self.session.add(user)
        await self.session.commit()
        return user

    async def get_user(self, uid: int) -> User | None:
        with suppress(NoResultFound):
            query = select(User).where(User.uid == uid)
            res = await self.session.execute(query)
            user = res.scalars().one()
            return user
        
    async def commit(self):
        await self.session.commit()

class UserManager(BaseManager):
    async def set_locale(self, locale: str, user: User, db: Database) -> None:
        user.language = locale
        await db.commit()

    async def get_locale(self, event_from_user, db: Database) -> str:
        uid = event_from_user.id
        return await db.get_user(uid)