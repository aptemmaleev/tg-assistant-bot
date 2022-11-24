from random import randint

from telegram import InputFile
from config import config
from aiogram import Bot, Dispatcher, types

from .utils.user import BotUser
from .utils.db import PostgresDatabase
from .utils.cache import Cache

from filters.permissions import check_role


from modules.elements.keyboards import start_verification_keyboard

class HelpModule():
    def __init__(self, dp: Dispatcher, bot: Bot):
        self.dp = dp
        self.bot = bot
        
        dp.register_message_handler(self.help_command, commands=["help", "info", "помощь", "хелп"])
    
    # Help command
    async def help_command(self, message: types.Message):
        # Only if user is admin or teacher
        if (not check_role(message, ['admin', 'teacher'])):
            answer = "*Сначала получите доступ к боту\\!* \n"
            answer += "Выполните команду: /start"
            await message.answer(answer = answer, parse_mode="MarkdownV2")
            return
        
        # Process help command        
        help_text = '📕*Список комманд:* \n'
        help_text += '📌 /menu \\- меню бота\n'
        await message.answer(help_text, parse_mode='MarkdownV2')

def setup(dp: Dispatcher, bot):
    HelpModule(dp, bot)