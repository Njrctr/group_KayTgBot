from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsModeratedTread(BaseFilter):
    async def __call__(self, message: Message, moderated_tread: int | None):
        if moderated_tread is None:
            return True
        if moderated_tread is not None:
            if moderated_tread == message.message_thread_id:
                return True
            else:
                return False
            
        
class IsModeratedTreadFinal(BaseFilter):
    async def __call__(self, message: Message, moderated_tread: int | None):
        if moderated_tread is None:
            return False
        else:
            if moderated_tread == message.message_thread_id and license:
                return True
            else:
                return False
