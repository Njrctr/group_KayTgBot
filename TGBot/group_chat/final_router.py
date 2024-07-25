from aiogram import F, Router
from aiogram.types import Message
from TGBot.filters.is_moderated_tread import IsModeratedTreadFinal
from TGBot.filters.is_admin import IsAdmin


end_router = Router()
end_router.message.filter(F.chat.type.in_({"group", "supergroup"}))


@end_router.message(IsModeratedTreadFinal(), ~IsAdmin())
async def message_in_tread_not_handled(message: Message):
    await message.delete()
