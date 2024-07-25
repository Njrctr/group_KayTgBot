from database.cash import RedisClient
from database.repository import UserRepository, BannedStickerRepository
from config.configuration import config

cash = RedisClient(1)


async def on_startup():
    users = [user.tg_id for user in await UserRepository.get_all_users()]
    await cash.set("users", users, serial=True)
    banned_stickers = [sticker.set_name for sticker in await BannedStickerRepository.get_all_stickers()]
    await cash.set("banned_stickers", banned_stickers, serial=True)
    await cash.set("moderated_tread", config.TELEGRAMBOT.MODERATED_TREAD)
    await cash.set("moderated_tread", config.TELEGRAMBOT.HELLO_MESSAGE)
    # await cash.set("groups", [group.chat_id for group in groups], serial=True)
    # return [group.chat_id for group in groups]
    pass


async def on_shutdown():
    pass
