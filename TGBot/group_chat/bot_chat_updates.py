from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, \
    LEAVE_TRANSITION, IS_NOT_MEMBER, MEMBER, ADMINISTRATOR
from aiogram import F, Router
from aiogram.types import ChatMemberUpdated


bot_updates = Router()
bot_updates.my_chat_member.filter(F.chat.type.in_({"group", "supergroup"}))


@bot_updates.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> (MEMBER | ADMINISTRATOR)))
async def bot_join_to_group(event: ChatMemberUpdated):
    await event.answer("Привет! Меня зовут Кай, я ваш личный помощник")


@bot_updates.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION))
async def bot_leave_from_group(event: ChatMemberUpdated):
    print(f"Лол меня кикнули из {event.chat.id}")
