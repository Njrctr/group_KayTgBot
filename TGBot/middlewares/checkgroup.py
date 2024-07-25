from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message
import logging
from aiogram.enums import ChatMemberStatus
from database.cash import RedisClient
from database.utils.bot_utils import on_startup

cash = RedisClient(1)


class CheckGroup(BaseMiddleware):
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
        # admins = await cash.get(str(event.chat.id) + "_admins", serial=True)
        # if not admins:
        #     admins = await bot.get_chat_administrators(event.chat.id)
        #     admins = [admin.user.id for admin in admins]
        #     await cash.set(str(event.chat.id) + "_admins", admins, serial=True, ex=1440)
        # if bot.id not in admins:
        #     return
        #
        # groups = await cash.get("groups", serial=True)
        # if groups is None:
        #     groups = await on_startup()
        # if event.chat.id not in groups:
        #     admins = await bot.get_chat_administrators(event.chat.id)
        #     creator = list(filter(lambda x: x.status is ChatMemberStatus.CREATOR, admins))[0].user
        #     await GroupRepository.add_new_group(event.chat.id, creator)
        #     await on_startup()
        return await handler(event, data)
