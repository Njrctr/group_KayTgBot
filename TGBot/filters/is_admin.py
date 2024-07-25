from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram import Bot
from config.configuration import config
from database.cash import RedisClient

cash = RedisClient(1)


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message, bot: Bot):  # Проверка на администратора
        admins = await cash.get("chat_admins", serial=True)
        if admins is None:
            admins = await bot.get_chat_administrators(message.chat.id)
            admins = [admin.user.id for admin in admins]
            await cash.set("chat_admins", admins, serial=True)
        return message.from_user.id in admins


class IsCreator(BaseFilter):
    async def __call__(self, message: Message):  # Проверка на владельца чата
        creator = cash.get("creator")
        return message.from_user.id == creator


class IsAbsoluteAdmin(BaseFilter):
    async def __call__(self, message: Message, bot: Bot):  # Проверка на абсолютного администратора
        if message.from_user.id in config.TELEGRAMBOT.ADMINS:
            return True
