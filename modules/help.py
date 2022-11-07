from random import randint
from config import config
from aiogram import Bot, Dispatcher, types

from utils.user import BotUser
from utils.db import PostgresDatabase
from utils.cache import Cache

from modules.elements.keyboards import start_verification_keyboard

class HelpModule():
    def __init__(self, dp: Dispatcher, bot: Bot):
        self.dp = dp
        self.bot = bot
        
        dp.register_message_handler(self.help_command, role=["teacher", "admin"], commands=["help", "info", "помощь", "хелп"])
    
    async def help_command(self, message: types.Message):
        print(Cache.get_user(message.from_id))
        
        help_text = ''
        help_text += '📕*Список комманд:* \n'
        help_text += '📌 /codeforces \\- панель управления CodeForces  \n'
        help_text += '📌 /onlinegdb \\- панель управления OnlineGdb Classroom  \n'
        help_text += '📌 /acmp \\- панель управления Acmp  \n'
        help_text += '📌 /sheets \\- панель управления Google Sheets \\(Журнал\\)  \n'
        await message.answer(help_text, parse_mode='MarkdownV2')

def setup(dp: Dispatcher, bot):
    HelpModule(dp, bot)