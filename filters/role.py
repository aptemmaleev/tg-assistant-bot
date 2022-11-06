from typing import Union
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import BoundFilter

from config import config

class TeacherFilter(BoundFilter):
    key = 'is_teacher'
    
    def __init__(self, is_teacher: bool):
        self.teachers = [1234, 11111]
        self.is_teacher = is_teacher
    
    async def check(self, obj: Union[types.Message, types.CallbackQuery]):
        user = obj.from_user
        if (user.id in self.teachers):
            return self.is_teacher is True
        else:
            return self.is_teacher is False
        
class OwnerFilter(BoundFilter):
    key = 'is_owner'
    
    def __init__(self, is_owner: bool):
        self.owner_id = config.owner
        self.is_owner = is_owner

    async def check(self, obj: Union[types.Message, types.CallbackQuery]):
        user = obj.from_user
        if (user.id == self.owner_id):
            return self.is_owner is True
        else:
            return self.is_owner is False

def setup_permissions(dp: Dispatcher):
    dp.filters_factory.bind(OwnerFilter, event_handlers=[dp.message_handlers, dp.callback_query_handlers])
    dp.filters_factory.bind(TeacherFilter, event_handlers=[dp.message_handlers, dp.callback_query_handlers])