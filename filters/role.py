from typing import List, Union
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import BoundFilter

from utils.db import PostgresDatabase
from utils.cache import Cache

from config import config

class RoleFilter(BoundFilter):
    """
    Check user role
    """
    
    key = 'role'
    
    def __init__(self, role: Union[str, List[str]]) -> None:
        if isinstance(role, str):
            self.role = [role]
        elif isinstance(role, list):
            self.role = role
        else:
            raise ValueError(
                f"filter role must be a str or list of str, not {type(role).__name__}"
            )
    
    async def check(self, obj: Union[types.Message, types.CallbackQuery]):
        user = Cache.get_user(obj.from_user.id)
        if (type(self.role) == str and user.role_name == self.role):
            return True
        elif(type(self.role) == list and user.role_name in self.role):
            return True
        return False
        
        

class TeacherFilter(BoundFilter):
    key = 'is_teacher'
    
    def __init__(self, is_teacher: bool):
        self.teachers = [1234, 11111]
        self.is_teacher = is_teacher
    
    async def check(self, obj: Union[types.Message, types.CallbackQuery]):
        user = obj.from_user
        user = PostgresDatabase.get_user(user.id)
        if (user[2]):
            print('is teacher')
            return self.is_teacher is True
        else:
            print('not teacher')
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
    dp.filters_factory.bind(RoleFilter, event_handlers=[dp.message_handlers, dp.callback_query_handlers])