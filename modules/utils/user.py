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
    gdb: str
    """OnlineGDB classroom id"""
    acmp: bool
    """Acmp enabled"""
    
    def __init__(self, id: int, name: str, sheets: str, gdb: str, acmp: bool):
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
        self.acmp = acmp

class BotUser():
    id: int                      # Telegram user id
    first_access: datetime       # First interaction with bot
    role_name: str               # Role name
    role_description: str        # Role description
    groups: List[Group]          # List of groups
    
    def __init__(self, id: int):
        self.id = id
        self.load()

    def load(self):
        data = PostgresDatabase.get_user(self.id)
        
        self.first_access = data['first_access']             
        self.role_name = data['role']['name']
        self.role_description = data['role']['description']
                
        self.groups: List = []
        if (data['groups'] == None):
            return
        for row_group in data['groups']:
            print(row_group['name'])
            self.groups.append(Group(row_group['id'], 
                                     row_group['name'],
                                     row_group['sheets'],
                                     row_group['gdb'],
                                     row_group['acmp']))
    
    def add_group(self, name: str, sheets_id: str):
        PostgresDatabase.add_group(self.id, name, sheets_id)
        self.load()
    
    def get_request(self):
        return PostgresDatabase.get_verification_request_by_id(self.id)
    
    def add_request(self, code: str):
        return PostgresDatabase.add_verification_request(self.id, code)
    
    def del_request(self):
        PostgresDatabase.delete_verification_request(self.id)
    
    def set_role(self, role_name: str):
        PostgresDatabase.set_role(self.id, role_name)
        self.load()
