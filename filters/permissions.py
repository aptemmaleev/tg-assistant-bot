from typing import List, Union
from aiogram import types

from modules.utils.cache import Cache

def check_role(obj: Union[types.Message, types.CallbackQuery], roles: Union[str, list]):    
    user = Cache.get_user(obj.from_user.id)
    if (type(roles) == str):
        if (roles == user.role_name):
            return True
    elif(type(roles) == list):
        if (user.role_name in roles):
            return True
    return False