from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from database.cash import RedisClient
from database.database_build import async_session_factory
from database.models import UsersOrm, BannedStickersOrm, FunAnswersOrm
from aiogram.types import User
import logging

cash = RedisClient(1)


class UserRepository:
    
    @staticmethod
    async def add_new_user(user: User):
        """Создаёт новую запись о пользователе в таблице users"""
        async with async_session_factory() as session:
            haven_user = select(UsersOrm).filter_by(tg_id=user.id)
            haven_user = (await session.execute(haven_user)).unique().scalar_one_or_none()
            if haven_user is None:
                user = UsersOrm(tg_id=user.id, username=user.username, name=user.full_name)
                session.add(user)
                await session.commit()
                logging.info(f"Создан новый пользователь {user.tg_id}")

    @staticmethod
    async def get_user_by_id(user_id: int):
        """Возвращает Юзера по его id"""
        async with async_session_factory() as session:
            user_query = (
                select(UsersOrm)
                .filter_by(tg_id=user_id)
            )
            user = (await session.execute(user_query)).scalar_one_or_none()
            print(user.user_groups)
            return False if user is None else user

    @staticmethod
    async def get_all_users() -> list[UsersOrm]:
        """Возвращает всех юзеров"""
        async with async_session_factory() as session:
            query = select(UsersOrm)
            users = (await session.execute(query)).scalars().all()
            return users

    @staticmethod
    async def delete_user(user_id: int):
        """Удаляет юзера"""
        async with async_session_factory() as session:
            query = (
                select(UsersOrm)
                .filter_by(tg_id=user_id)
            )
            user = (await session.execute(query)).scalar_one()
            await session.delete(user)
            await session.commit()

    @staticmethod
    async def set_user_nickname(user_id: int, new_nickname: str):
        """Устанавливает пользователю Никнейм в группе"""
        async with async_session_factory() as session:
            query = (
                select(UsersOrm)
                .filter_by(tg_id=user_id)
            )
            user = (await session.execute(query)).scalar_one_or_none()
            user.nickname = new_nickname
            await session.commit()
            logging.debug(f"Пользователю {user_id} установлен никнейм {new_nickname}")


class BannedStickerRepository:
            
    @staticmethod
    async def add_sticker_in_ban(sticker_setname: str):
        """Добавляет стикер в банлист группы"""
        async with async_session_factory() as session:
            query = (
                select(BannedStickersOrm)
                .filter_by(set_name=sticker_setname)
            )
            sticker_exists = (await session.execute(query)).scalar_one_or_none()
            if sticker_exists is not None:
                return
            new_sticker = BannedStickersOrm(set_name=sticker_setname)
            session.add(new_sticker)
            await session.commit()

    @staticmethod
    async def get_all_stickers() -> list[BannedStickersOrm]:
        """Возвращает список всех стикеров в бане"""
        async with async_session_factory() as session:
            query = select(BannedStickersOrm)
            stickers_list = (await session.execute(query)).scalars().all()
            return stickers_list

    @staticmethod
    async def delete_sticker_from_ban(sticker_setname: str):
        """Удаляет стикерпак из банлиста группы"""
        async with async_session_factory() as session:
            query = (
                select(BannedStickersOrm)
                .filter_by(set_name=sticker_setname)
            )
            sticker_exist = (await session.execute(query)).scalar_one_or_none()

            if sticker_exist is None:
                return
            await session.delete(sticker_exist)
            await session.commit()


class FunsRepository:
    
    @staticmethod
    async def add_new_answer(answer_in: list[str] | str):
        async with async_session_factory() as session:
            
            if isinstance(answer_in, list):
                new_answer = [FunAnswersOrm(answer=item) for item in answer_in]
                session.add_all(new_answer)
            else:
                new_answer = FunAnswersOrm(answer=answer_in)
                session.add(new_answer)
            await session.commit()
            
    @staticmethod
    async def get_all_answers():
        async with async_session_factory() as session:
            answers = (await session.execute(select(FunAnswersOrm))).scalars().all()
            return answers
        
    @staticmethod
    async def get_user_fun_answer(user_id: int) -> str | None:

        async with async_session_factory() as session:
            query = (
                select(UsersOrm)
                .filter_by(tg_id=user_id)
            )
            user = (await session.execute(query)).scalar_one()
            date = datetime.today().date()
            if (user.fun_answer is None) or (user.fun_answer_date != date):
                return None
            elif user.fun_answer_date == date:
                return user.fun_answer
                
    @staticmethod
    async def set_user_fun_answer(user_id: int, chat_id: int, fun: str) -> None:
        async with async_session_factory() as session:
            query = (
                select(UsersOrm)
                .filter_by(tg_id=user_id)
            )
            user = (await session.execute(query)).scalar_one()
            date = datetime.today().date()
            user.fun_answer = fun
            user.fun_answer_date = date
            await session.commit()
