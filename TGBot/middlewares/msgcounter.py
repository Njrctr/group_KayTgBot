from datetime import datetime
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject,  Message
import logging
from database.repository import UserRepository
from aiogram.enums import ChatMemberStatus
from database.cash import RedisClient

cash = RedisClient(1)


class CounterMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        bot: Bot = data["bot"]
        if event.from_user.id == bot.id:
            return
        if event.from_user.full_name in ["Channel", "Telegram"]:
            return
        if event.chat.type == 'private': 
            logging.debug("This is private chat!")
            return await handler(event, data)

        users = await cash.get("users", serial=True)
        if event.from_user.id not in users:
            await UserRepository.add_new_user(event.from_user)
            new_users = [user.tg_id for user in await UserRepository.get_all_users()]
            await cash.set("users", new_users, serial=True)

        data['moderated_tread'] = await cash.get("moderated_tread", serial=True)
        # group_data = await cash.get(str(event.chat.id)+"_data", serial=True)
        # if group_data is None:
        #     group = await GroupRepository.get_group(event.chat.id, with_license=True)
        #     current_license = False if group.current_license is None \
        #         else group.current_license.end_of_license > datetime.today().date()
        #     group_dto = GroupWithUsersAndLicenseDTO.model_validate(group, from_attributes=True)
        #     group_data = group_dto.model_dump()
        #     group_data['group_users'] = [user['tg_id'] for user in group_data['group_users']]
        #     await cash.set(str(event.chat.id) + "_data", group_data, serial=True, ex=2000)
        # if event.from_user.id not in group_data["group_users"]:
        #     user = await UserRepository.add_new_user(event.from_user)
        #     await GroupRepository.append_user_in_group(user.tg_id, event.chat.id)
        #     group_data['group_users'].append(user.tg_id)
        #     await cash.set(str(event.chat.id) + "_data", group_data, ex=2000, serial=True)
        #
        # if event.text:
        #     len_of_text = len(event.text)
        # else:
        #     len_of_text = 1
        # await GroupRepository.msg_counter(event.chat.id, event.from_user.id, symbol_count=len_of_text)
        #
        # data['use_links'] = group_data['use_links']

        return await handler(event, data)
