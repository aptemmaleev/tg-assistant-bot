from random import randint
from config import config
from aiogram import Bot, Dispatcher, types
from .utils.cache import Cache

from .utils.db import PostgresDatabase
from .elements.keyboards import start_verification_keyboard

from filters.permissions import check_role

class OnlineGdbModule():
    def __init__(self, dp: Dispatcher, bot: Bot):
        self.dp = dp
        self.bot = bot
        
        # dp.register_message_handler(self.accept_verification_request, is_owner=True, commands=["accept"])
        # dp.register_message_handler(self.welcome_message, commands=["start", "help"])
        # dp.register_callback_query_handler(self.process_start_verification_button, lambda c: c.data == 'start_verification_button')
    
    # # Start command handler
    # async def welcome_message(self, message: types.Message):
    #     # Get user from database
    
    # Onlinegdb command
    async def onlinegdb_command(self, message: types.Message):
        # Only for admins and teachers
        if (not check_role(message, 'admin', 'teacher')):
            return
        
        # If user.groups empty
        user = Cache.get_user(message.from_id)
        if (len(user.groups) == 0):
            answer = "*Вы еще не добавили ни одну группу\\!* \n"
            answer += "Выполните команду /group"
            await message.answer(answer = answer, parse_mode="MarkdownV2")
        
def setup(dp: Dispatcher, bot):
    OnlineGdbModule(dp, bot)