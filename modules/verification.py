from random import randint
from config import config
from aiogram import Bot, Dispatcher, types

from .utils.cache import Cache

from .elements.keyboards import start_verification_keyboard
from filters.permissions import check_role

class VerificationModule():
    def __init__(self, dp: Dispatcher, bot: Bot):
        self.dp = dp
        self.bot = bot
        
        dp.register_message_handler(self.start_command, commands=["start", "старт", "начало"])
        dp.register_callback_query_handler(self.start_verification_callback, lambda c: c.data == 'start_verification_button')
        
    # Welcome message (/start)
    async def start_command(self, message: types.Message):
        # User already have access
        if (check_role(message, ['teacher', 'admin'])):
            answer = "*Вы уже получили доступ к боту\\!* \n"
            answer += "Список команд: /help"
            await message.answer(answer, parse_mode="MarkdownV2")
            return
        
        # User is rejected
        elif(check_role(message, 'rejected')):
            return
        
        # Default user
        user = Cache.get_user(message.from_id)
        if (user.get_request() == None):
            answer = f"*Добро пожаловать, {message.from_user.first_name}*\\! \n"
            answer += "Чтобы начать пользоваться ботом необходимо пройти верификацию\\."
            await message.answer(answer, parse_mode="MarkdownV2", reply_markup=start_verification_keyboard)
        else:
            answer = f'Ранее вы уже оставили заявку №`{user.get_request()}`\n'
            answer += 'Сообщите уникальный код @aptemm, если вы этого еще не сделали\\.'
            await self.bot.send_message(message.from_id, answer, parse_mode="MarkdownV2")
        
        
        
    # # Start command handler
    # async def welcome_message(self, message: types.Message):
    #     # User is teacher or not
    #     if (check_role(message, ['teacher', 'admin'])):
    #         answer = "*Вы уже получили доступ к боту\\!* \n"
    #         answer += "Список команд: /help"
    #         await message.answer(answer, parse_mode="MarkdownV2")
    #         return
    #     # Get user from database
    #     user = Cache.get_user(message.from_id)
    #     if (user.get_request() == None):
    #         answer = f"*Добро пожаловать, {message.from_user.first_name}*\\! \n"
    #         answer += "Чтобы начать пользоваться ботом необходимо пройти верификацию\\."
    #         await message.answer(answer, parse_mode="MarkdownV2", reply_markup=start_verification_keyboard)
    #     else:
    #         await self.bot.send_message(message.from_id, 
    #                                     f'Ранее вы уже оставили заявку №`{user.get_request()}`\n' +
    #                                     'Сообщите уникальный код @aptemm, если вы этого еще не сделали\\.',
    #                                     parse_mode="MarkdownV2")
    
    
    async def start_verification_callback(self, callback_query: types.CallbackQuery):
        # Answer callback
        await self.bot.answer_callback_query(callback_query.id)
        
        # User already have access
        if (check_role(callback_query, ['teacher', 'admin'])):
            answer = "*Вы уже получили доступ к боту\\!* \n"
            answer += "Список команд: /help"
            await callback_query.message.edit_text(answer = answer, parse_mode="MarkdownV2")
            return
        
        # Only guest
        if (not check_role(callback_query, 'guest')):
            answer = "*Недоступно\\!*"
            await callback_query.message.edit_text(answer = answer, parse_mode="MarkdownV2")
            return

        # Start verification process
        user = Cache.get_user(callback_query.from_user.id)
        if (user.get_request() == None):
            # first code message
            answer = 'Вам будет выслан уникальный код заявки\\. Сообщите его @aptemm\\.'
            await callback_query.message.answer(answer, parse_mode="MarkdownV2")
            # random code generator
            code = randint(100000, 999999)
            user.add_request(code)
            # second code message
            await callback_query.message.answer(f'Ваш код: `{code}`', parse_mode="MarkdownV2")
        else:
            answer = f'Ранее вы уже оставили заявку №`{user.get_request()}`\n'
            answer += 'Сообщите уникальный код @aptemm, если вы этого еще не сделали\\.'
            await callback_query.message.edit_text(answer, parse_mode="MarkdownV2")
        
    # # start_verification_button Query Callback 
    # async def process_start_verification_button(self, callback_query: types.CallbackQuery):
    #     await self.bot.answer_callback_query(callback_query.id)
    #     # User already have access
    #     if (check_role(callback_query, ['teacher', 'admin'])):
    #         await callback_query.message.edit_text("*Вы уже получили доступ к боту\\!* \n" +
    #                                                "Список команд: /help", parse_mode="MarkdownV2")
    #         return
        
    #     user = Cache.get_user(callback_query.from_user.id)
    #     if (user.get_request() == None):
    #         await self.bot.send_message(callback_query.from_user.id, 
    #                                     'Вам будет выслан уникальный код заявки\\. Сообщите его @aptemm\\.',
    #                                     parse_mode="MarkdownV2")
    #         code = randint(100000, 999999)
    #         user.add_request(code)
    #         await self.bot.send_message(callback_query.from_user.id, 
    #                                     f'Ваш код: `{code}`',
    #                                     parse_mode="MarkdownV2")
    #     else:
    #         await self.bot.send_message(callback_query.from_user.id, 
    #                                     f'Ранее вы уже оставили заявку №`{user.get_request()}`\n' +
    #                                     'Сообщите уникальный код @aptemm, если вы этого еще не сделали\\.',
    #                                     parse_mode="MarkdownV2")
        
def setup(dp: Dispatcher, bot):
    VerificationModule(dp, bot)