from aiogram.filters import BaseFilter
from aiogram.types import Message

from database.cash import RedisClient
from database.repository import BannedStickerRepository

cash = RedisClient(1)


class StickerFilter(BaseFilter):
    
    async def __call__(self, message: Message) -> bool:
        banned_stickers = await cash.get("banned_stickers", serial=True)
        if message.sticker.set_name in banned_stickers:
            return True
