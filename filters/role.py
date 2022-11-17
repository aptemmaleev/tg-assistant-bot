from typing import List, Union
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import BoundFilter

from modules.utils.db import PostgresDatabase
from modules.utils.cache import Cache

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

def setup_permissions(dp: Dispatcher):
    dp.filters_factory.bind(RoleFilter, event_handlers=[dp.message_handlers, dp.callback_query_handlers])