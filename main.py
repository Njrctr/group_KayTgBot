import logging
import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis, DefaultKeyBuilder
from TGBot.group_chat.members_commands import member_command
from TGBot.group_chat.events import events_router
from TGBot.group_chat.admins_commands import admins_command
from TGBot.group_chat.final_router import end_router
from TGBot.middlewares.msgcounter import CounterMiddleware
from TGBot.middlewares.checkgroup import CheckGroup
from TGBot.group_chat.bot_chat_updates import bot_updates
from config.configuration import config
# from TGBot.private_chat.menu.main_menu import main_menu_router
from aiogram_dialog import setup_dialogs
import eventlet
from database.utils.bot_utils import on_startup
eventlet.monkey_patch()


storage = RedisStorage(
    redis=Redis(host='localhost'),
    key_builder=DefaultKeyBuilder(with_destiny=True)
    )

bot = Bot(config.TELEGRAMBOT.KEY)
dp = Dispatcher(storage=storage)


async def main():
    # dp.include_router(main_menu_router)
    dp.include_router(bot_updates)
    # dp.message.outer_middleware(CheckGroup())
    dp.message.outer_middleware(CounterMiddleware())
    
    dp.include_router(member_command)
    dp.include_router(events_router)
    dp.include_router(admins_command)
    dp.include_router(end_router)
    setup_dialogs(dp)
    await bot.delete_webhook(True)
    await on_startup()
    await dp.start_polling(
        bot,
        polling_timeout=500,
        relax=0.5,
        allowed_updates=["message", "inline_query", "chat_member", "callback_query"],
        skip_updates=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
