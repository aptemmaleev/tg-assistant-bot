from typing import List

from aiogram.types import User

from .user import BotUser
from .db import PostgresDatabase

class Cache:
    __instance = None
    __users: dict

    def __new__(cls):
        if cls.__instance == None:
            cls.__instance = super(Cache, cls).__new__(cls)
            cls.__users = dict()
        return cls.__instance
    
    @classmethod
    def get_user(cls, id: int):
        id = int(id)
        if id in cls.__users:
            return cls.__users[id]
        user = BotUser(id)
        cls.__users[id] = user
        return user