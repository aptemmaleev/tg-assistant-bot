from random import randint
from config import config
from aiogram import Bot, Dispatcher, types

from utils.db import PostgresDatabase
from modules.elements.keyboards import start_verification_keyboard

class VerificationModule():
    def __init__(self, dp: Dispatcher, bot: Bot):
        self.dp = dp
        self.bot = bot
        
        dp.register_message_handler(self.accept_verification_request, is_owner=True, commands=["accept"])
        dp.register_message_handler(self.welcome_message, commands=["start"])
        dp.register_callback_query_handler(self.process_start_verification_button, lambda c: c.data == 'start_verification_button')
        
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
            await message.answer(answer, parse_mode="MarkdownV2")
        else:
            request = PostgresDatabase.get_verification_request_by_id(message.from_id)
            if (request == None):
                answer += f"*Добро пожаловать, {message.from_user.first_name}*\\! \n"
                answer += "Чтобы начать пользоваться ботом необходимо пройти верификацию\\."
                await message.answer(answer, parse_mode="MarkdownV2", reply_markup=start_verification_keyboard)
            else:
                await self.bot.send_message(message.from_id, 
                                            f'Ранее вы уже оставили заявку №`{request[1]}`\n' +
                                            'Сообщите уникальный код @aptemm, если вы этого еще не сделали\\.',
                                            parse_mode="MarkdownV2")
    
    # start_verification_button Query Callback 
    async def process_start_verification_button(self, callback_query: types.CallbackQuery):
        db_user = PostgresDatabase.get_user(callback_query.from_user.id)
        if (db_user[2]):
            await callback_query.answer('У вас уже есть доступ')
            return
        await self.bot.answer_callback_query(callback_query.id)
        request = PostgresDatabase.get_verification_request_by_id(callback_query.from_user.id)
        if (request == None):
            await self.bot.send_message(callback_query.from_user.id, 
                                        'Вам будет выслан уникальный код заявки\\. Сообщите его @aptemm\\.',
                                        parse_mode="MarkdownV2")
            code = randint(100000, 999999)
            PostgresDatabase.add_verification_request(callback_query.from_user.id, code)
            await self.bot.send_message(callback_query.from_user.id, 
                                        f'Ваш код: `{code}`',
                                        parse_mode="MarkdownV2")
        else:
            await self.bot.send_message(callback_query.from_user.id, 
                                        f'Ранее вы уже оставили заявку №`{request[1]}`\n' +
                                        'Сообщите уникальный код @aptemm, если вы этого еще не сделали\\.',
                                        parse_mode="MarkdownV2")
    
    # Request accept command handler
    async def accept_verification_request(self, message: types.Message):
        args = message.get_args()
        # Args is empty
        if (args == ''):
            await message.answer('Введите номер заявки: `/accept id`', parse_mode="MarkdownV2")
            return
        # Args is not digit
        args = args.split()[0]
        if not args.isdigit():
            await message.answer('Введите номер заявки: `/accept id`', parse_mode="MarkdownV2")
            return
        # Process
        code = int(args)
        request = PostgresDatabase.get_verification_request_by_code(code)
        if (request == None):
            await message.answer(f'В базе нет такой заявки `{code}`', parse_mode="MarkdownV2")
            return
        PostgresDatabase.delete_verification_request(request[0])
        PostgresDatabase.set_teacher(request[0])
        await self.bot.send_message(request[0], 'Ваша заявка рассмотрена! Вы получили доступ к основным функциям бота /help')
        await message.answer('Done')
        
def setup(dp: Dispatcher, bot):
    VerificationModule(dp, bot)