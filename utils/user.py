#from config import config
from typing import List

from aiogram import Bot, Dispatcher
from aiogram.types import User

from .db import PostgresDatabase

from datetime import datetime

class Group():
    id: int
    """Group id in database"""
    name: str 
    """Group name"""
    sheets: str
    """Google Sheets id"""
    classroom: str
    """OnlineGDB classroom id"""
    
    def __init__(self, id: int, name: str, sheets: str, gdb: str):
        """School group

        Args:
            id (int): Group id in database
            name (str): Name of the group
            sheets (str): Google sheets id
            gdb (str): OnlineGDB classroom id
        """
        self.id = id
        self.name = name
        self.sheets = sheets
        self.gdb = gdb

class BotUser():
    id: int                      # Telegram user id
    first_access: datetime       # First interaction with bot
    role_name: str               # Role name
    role_description: str        # Role description
    groups: List[Group]          # List of groups
    
    def __init__(self, id: User):
        data = PostgresDatabase.get__user(id)
        
        self.id = id
        self.first_access = data['first_access']             
        self.role_name = data['role']['name']
        self.role_description = data['role']['description']
        
        self.groups: List = []
        if (data['groups'] == None):
            return
        for row_group in data['groups']:
            self.groups.append(Group(row_group['id'], 
                                     row_group['name'],
                                     row_group['sheets'],
                                     row_group['gdb']))

    # def __str__(self) -> str:
    #     text = ''
    #     text += f'user: {self.user.id}\n'
    #     text += f'first_access: {self.first_access}\n'
    #     text += f'role_name: {self.role_name}\n'
    #     text += f'role_description: {self.role_description}\n'
    #     text += 'groups:\n'
    #     for group in self.groups:
    #         text += f'  id: {group.id}\n'
    #         text += f'  name: {group.name}\n'
    #         text += f'  sheets: {group.sheets}\n'
    #         text += f'  classroom: {group.classroom}\n'
    #     return text