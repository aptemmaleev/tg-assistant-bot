from config import config
from utils.db import PostgresDatabase
from aiogram import Bot, Dispatcher, types

from utils.buttons import start_verification_keyboard

class VerificationModule():
    def __init__(self, dp: Dispatcher, bot: Bot):
        self.dp = dp
        self.bot = bot
        
        dp.register_message_handler(self.welcome_message, commands=["start", "help"])
        dp.register_callback_query_handler(self.process_start_verification_button, 
                                           lambda c: c.data == 'start_verification_button')
        
    # Start command handler
    async def welcome_message(self, message: types.Message):
        # Get user from database
        db_user = PostgresDatabase.get_user(message.from_id)
        if (db_user == None):
            db_user = PostgresDatabase.add_user(message.from_id)
        # User is teacher or not
        answer = ""
        if (db_user[2]):
            answer += "*Вы уже получили доступ к боту\\!* \n"
            answer += "Список команд: /help"
        else:
            answer += f"*Добро пожаловать, {message.from_user.first_name}*\\! \n"
            answer += "Чтобы начать пользоваться ботом необходимо пройти верификацию\\."
        await message.answer(answer, parse_mode="MarkdownV2", reply_markup=start_verification_keyboard)
    
    # start_verification_button Query Callback 
    async def process_start_verification_button(self, callback_query: types.CallbackQuery):
        await self.bot.answer_callback_query(callback_query.id)
        answer = 'Вам будет выдан уникальный код заявки. Сообщите его @aptemm.'
        await self.bot.send_message(callback_query.from_user.id, answer)
    
def setup(dp: Dispatcher, bot):
    VerificationModule(dp, bot)