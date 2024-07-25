from aiogram import Router, F, Bot
from aiogram.types import Message, ChatPermissions
import re
from datetime import datetime, timedelta
from aiogram.filters.command import Command, CommandObject
from TGBot.filters.is_admin import IsAdmin
from database.cash import RedisClient
from database.repository import BannedStickerRepository
from aiogram.exceptions import TelegramForbiddenError

admins_command = Router()
admins_command.message.filter(F.chat.type.in_({"group", "supergroup"}))
admins_command.message.filter(IsAdmin())
cash = RedisClient(1)


@admins_command.message(F.text.lower().regexp("^кай бан пак\\s"))
async def ban_stickerset(message: Message):
    sticker_set = message.text[re.match("^кай бан пак\\s", message.text.lower()).span()[1]:]
    await BannedStickerRepository.add_sticker_in_ban(sticker_set)
    new_banned_stickers = [sticker.set_name for sticker in await BannedStickerRepository.get_all_stickers()]
    await cash.set("banned_stickers", new_banned_stickers, serial=True)

    await message.reply(
        f"Пак стикеров <a href='https://t.me/addstickers/{sticker_set}'>{sticker_set}</a> \
больше не доступен для отправки в чате!",
        parse_mode='HTML',
        disable_web_page_preview=True)


@admins_command.message(F.text.lower().regexp("^кай разбан пак\\s"))    
async def unban_stickerset(message: Message):
    sticker_set = message.text[re.match("^кай разбан пак\\s", message.text.lower()).span()[1]:]
    await BannedStickerRepository.delete_sticker_from_ban(sticker_set)
    new_banned_stickers = [sticker.set_name for sticker in await BannedStickerRepository.get_all_stickers()]
    await cash.set("banned_stickers", new_banned_stickers, serial=True)
    await message.reply(
        f"Пак стикеров <a href='https://t.me/addstickers/{sticker_set}'>{sticker_set}</a> \
снова доступен в чате!",
        parse_mode='HTML',
        disable_web_page_preview=True)
        

@admins_command.message(Command('setname'))
async def get_sticker_set_name(message: Message):
    """Получить имя стикерпака при ответе на стикер""" 
    if (message.reply_to_message is None) or (message.reply_to_message.sticker is None):
        await message.reply(
            "Ошибка: Команда работает только при ответе на сообщение со стикером.",
            disable_notification=True)
        return
    set_name = message.reply_to_message.sticker.set_name
    await message.reply(set_name)


@admins_command.message(Command("chatinfo"))
async def get_info_a(message: Message, bot: Bot):
    data = f"""chat ID: `{message.chat.id}`, type: {message.chat.type}
tread ID: `{message.message_thread_id}`
Your user id: `{message.from_user.id}`"""
    try:
        await bot.send_message(chat_id=message.from_user.id, text=data, parse_mode="MARKDOWN")
    except TelegramForbiddenError:
        await message.reply(
            "Я не могу написать вам в ЛС, пожалуйста, \
создайте диалог со мной и повторите команду.",
            disable_notification=True)


@admins_command.message(Command('mute'))
async def mute_user(message: Message, command: CommandObject, bot: Bot):
    """Временное ограничение юзера"""
    if message.reply_to_message is None:
        await message.reply("Ошибка: Команда работает только при ответе на сообщение пользователя, \
которого вы собираетесь замьютить.")
        return
    victim_user_id = int(message.reply_to_message.from_user.id)
    if command.args is None:
        await message.reply(
            "Ошибка: Не переданы аргументы! \nПример: `/mute <time(минуты)>`")
        return
    try:
        delay_time = command.args.split(" ", maxsplit=1)[0]
        try:
            delay_time = int(delay_time)
        except Exception as ex:
            print("from admins_command.mute_user: ", ex)
            await message.reply("Ошибка: неправильный формат команды. параметр time должен быть целым числом!")
            return
    except ValueError:
        await message.reply(
            "Ошибка: неправильный формат команды. \nПример: `/mute <time(минуты)>`")
        return
    try:
        dt = datetime.now() + timedelta(minutes=delay_time)
        timestamp = dt.timestamp()
        await bot.restrict_chat_member(
            message.chat.id,
            victim_user_id,
            permissions=ChatPermissions(),
            until_date=int(timestamp))
        await message.reply(f"Пользователь не сможет писать в чат и отправлять медиафайлы {delay_time} мин!")
    except Exception as ex:
        print(ex)
        return await message.reply("Ошибка: Невозможно ограничить администратора!")
    

@admins_command.message(Command('ban'))
async def ban_user(message: Message, bot: Bot):
    """Бан юзера"""
    if message.reply_to_message is None:
        return await message.reply(
            "Ошибка: Команда работает только при ответе на сообщение пользователя, \
которого вы собираетесь забанить.")
    victim_user = message.reply_to_message.from_user
    victim_user_id = int(victim_user.id)
    try:
        await bot.ban_chat_member(chat_id=message.chat.id, user_id=victim_user_id)
        await message.reply(
            f"Пользователь <a href='tg://user?id={victim_user_id}'>{victim_user.full_name}</a>\
заблокирован!\nДля разблокировки: Manage group->Permissions->Removed users",
            parse_mode='HTML')
    except Exception as ex:
        print("from admins_command.ban_user:", ex)
        return await message.reply("Ошибка: Невозможно ограничить администратора!")


@admins_command.message(Command('kick'))
async def kick_user(message: Message, bot: Bot):
    """Кик юзера"""
    if message.reply_to_message is None:
        return await message.reply("Ошибка: Команда работает только при ответе на сообщение пользователя, \
которого вы собираетесь исключить.")
    victim_user = message.reply_to_message.from_user
    victim_user_id = int(victim_user.id)
    try:
        await bot.ban_chat_member(chat_id=message.chat.id, user_id=victim_user_id)
        await bot.unban_chat_member(chat_id=message.chat.id, user_id=victim_user_id)
        await message.reply(
            f"Пользователь <a href='tg://user?id={victim_user_id}'>{victim_user.full_name}</a>\
исключён, но всё ещё имеет возможность вступить в чат!",
            parse_mode='HTML')
    except Exception as ex:
        print("from admins_command.kick_user: ", ex)
        return await message.reply("Ошибка: Невозможно ограничить администратора!")
