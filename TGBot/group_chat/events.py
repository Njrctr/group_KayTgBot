from aiogram import Router, F, Bot
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, MEMBER, IS_NOT_MEMBER, \
    ADMINISTRATOR, RESTRICTED, CREATOR
from aiogram.types import ChatMemberUpdated

from database.cash import RedisClient
from database.repository import UserRepository


events_router = Router()
events_router.chat_member.filter(F.chat.type.in_({"group", "supergroup"}))

cash = RedisClient(1)


# Выходы и входы пользователя в чат
@events_router.chat_member(ChatMemberUpdatedFilter(
    member_status_changed=(IS_NOT_MEMBER | -RESTRICTED) >> (MEMBER | +RESTRICTED))
)
async def member_joined(event: ChatMemberUpdated, bot: Bot):
    await UserRepository.add_new_user(event.new_chat_member.user)
    new_users: list = (await cash.get("users", serial=True)).append(event.new_chat_member.user.id)
    await cash.set("users", new_users, serial=True)
    hello_message = await cash.get("hello_message")
    if hello_message is None:
        hello_message = ''
    await bot.send_message(
        event.chat.id,
        f"Привет, <a href='tg://user?id={event.new_chat_member.user.id}'>\
        {event.new_chat_member.user.full_name}</a>, добро пожаловать в чат!\n\n{hello_message}",
        parse_mode='HTML'
    )
    
    
@events_router.chat_member(ChatMemberUpdatedFilter(
    member_status_changed=(MEMBER | ADMINISTRATOR | +RESTRICTED) >> (IS_NOT_MEMBER | -RESTRICTED))
)
async def member_left(event: ChatMemberUpdated, bot: Bot):
    await bot.send_message(
        event.chat.id,
        f"Пользователь <a href='tg://user?id={event.new_chat_member.user.id}'>\
        {event.new_chat_member.user.full_name}</a> покинул чат. Очень жаль, он был моим другом...",
        parse_mode='HTML'
    )
    await UserRepository.delete_user(event.new_chat_member.user.id)
    new_users: list = (await cash.get("users", serial=True)).remove(event.new_chat_member.user.id)
    await cash.set("users", new_users, serial=True)


# @events_router.chat_member(ChatMemberUpdatedFilter(
#     member_status_changed=(MEMBER | ADMINISTRATOR) >> CREATOR)
# )
# async def creator_switch(event: ChatMemberUpdated):
#     await GroupRepository.edit_owner(event.chat.id, event.new_chat_member.user.id)
