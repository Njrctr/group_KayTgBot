from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import Message
import re
import json
import random

from TGBot.filters.is_moderated_tread import IsModeratedTread
from TGBot.group_chat.group_commands import all_commands
from TGBot.filters.sticker_inban import StickerFilter
from database.models import FunAnswersOrm
from database.repository import UserRepository, FunsRepository
from database.cash import RedisClient
from config.configuration import config

member_command = Router()
member_command.message.filter(F.chat.type.in_({"group", "supergroup"}))
cash = RedisClient(1)


@member_command.message(F.text.lower().regexp("^кай мне ник\\s"))
async def set_user_nickname(message: Message):
    new_nickname = message.text[re.match("^кай мне ник\\s", message.text.lower()).span()[1]:]
    if len(new_nickname) <= 16:
        await UserRepository.set_user_nickname(message.from_user.id, new_nickname)
        await message.reply(f"Вам установлен никнейм: {new_nickname}")
        await cash.delete("nicknames")
    else:
        await message.reply("Допустимая длина ника - 16 символов!")


# Команда Кай ники
@member_command.message(F.text.lower().regexp("^кай ники$"), IsModeratedTread())
async def get_all_nicknames(message: Message, use_links: bool = False):
    all_nicknames = await cash.get("nicknames", serial=True)
    if all_nicknames is not None:
        return await message.answer(all_nicknames, parse_mode="HTML", disable_notification=True)

    all_nicknames_list = await UserRepository.get_all_users()
    if all_nicknames_list is None:
        return await message.answer(text="Список пользователей пуст!")

    all_nicknames_string = "Список пользователей чата:\n\n"
    counter = 1
    for user in all_nicknames_list:
        if user.nickname is None:
            continue
        if use_links:
            all_nicknames_string += f"{counter}. <a href='tg://user?id={user.tg_id}'>{user.nickname}</a> \
- {user.name}\n"
        else:
            all_nicknames_string += f"{counter}. {user.nickname} - {user.name}\n"
        counter += 1

    await cash.set("nicknames", all_nicknames_string, serial=True)
    await message.answer(all_nicknames_string, parse_mode="HTML", disable_notification=True)


# Команда Кай кто я
@member_command.message(F.text.lower().regexp("^кай кто я$"), IsModeratedTread())
async def who_am_i(message: Message):
    answer: str = await cash.get(f"{message.from_user.id}_fun", serial=True)
    if answer is not None:
        return await message.reply(answer)

    answer: FunAnswersOrm = random.choice(await FunsRepository.get_all_answers())
    await FunsRepository.set_user_fun_answer(message.from_user.id, message.chat.id, answer.answer)
    date = datetime.now()
    date_tomorrow = datetime.date(date + timedelta(1))
    date_final = (datetime(date_tomorrow.year, date_tomorrow.month, date_tomorrow.day) - date).seconds
    await cash.set(f"{message.from_user.id}_fun", answer.answer, serial=True, ex=date_final)
    await message.reply(answer.answer)


@member_command.message(F.text.lower().regexp("^кай погода\\s"), IsModeratedTread())
async def get_weather(message: Message):

    city = message.text[re.match("^кай погода\\s", message.text.lower()).span()[1]:]
    for symbol in "0123456789!@#$%^&*()_!\"~`№;%:?*+'<>/|":
        if symbol in city:
            return await message.reply("Ошибка: недопустимые символы.")
    import aiohttp
    async with aiohttp.ClientSession() as session:
         # TODO Скрыть API ключ / Вынести в отдельную функцию
        async with session.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}\
&appid={config.WEATHER}&units=metric&lang=ru") as response:
            if response.status == 200:
                weather = await response.text()
                data = json.loads(weather)
                weather_data = f"""🌍 Погода в \'{data['name']}\' \n
Сейчас: {round(data['main']['temp'])}° ({data['weather'][0]['description'].capitalize()})
🫠Ощущается как: {round(data['main']['feels_like'])}°
💨 Ветер: {data['wind']['speed']} м/с
💧 Влажность: {data['main']['humidity']}%
☁ Облачность: {data['clouds']['all']}%
👀Видимость: {data['visibility']} м"""
                await message.reply(weather_data)
            else:
                await message.reply("Попробуйте снова, указав существующий город.")


@member_command.message(F.text.lower().regexp("^кай инфа\\s"), IsModeratedTread())
async def get_probability(message: Message):
    percent = random.randint(0, 100)
    await message.reply(f"Вероятность составляет: {percent}%!")


@member_command.message(F.text.lower().regexp("^кай выбери\\s"), IsModeratedTread())
async def go_choice(message: Message):
    what = message.text[re.match("^кай выбери\\s", message.text.lower()).span()[1]:].split(" или ")
    if len(what) == 1:
        await message.reply(f"Тяжелый выбор... пожалуй, {what[0]} ЛОЛ!")
        return
    random_choice = random.choice(what)
    await message.reply(f"Я выбираю: {random_choice}!")


@member_command.message(F.text.lower().regexp("^кай команды$"), IsModeratedTread())
async def get_commands(message: Message):
    await message.reply(all_commands, disable_notification=True, parse_mode="MarkdownV2")


# Получен стикер в групповом чате
@member_command.message(F.sticker, StickerFilter())
async def check_sticker(message: Message):
    await message.delete()
