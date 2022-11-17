from random import randint
from config import config
from aiogram import Bot, Dispatcher, types

from .utils.db import PostgresDatabase
from .utils.cache import Cache

from .elements.keyboards import start_verification_keyboard
from filters.permissions import check_role

class OwnerModule():
    def __init__(self, dp: Dispatcher, bot: Bot):
        self.dp = dp
        self.bot = bot
        
        dp.register_message_handler(self.owner_command, commands=["test"])
        dp.register_message_handler(self.accept_verification_request, commands=["accept"])
    
    async def owner_command(self, message: types.Message):
        if message.from_id != config.owner:
            return
        print(Cache.get_user(message.from_id))
        help_text = ''
        help_text += '📕*Список комманд:* \n'
        help_text += '📌 /codeforces \\- панель управления CodeForces  \n'
        help_text += '📌 /onlinegdb \\- панель управления OnlineGdb Classroom  \n'
        help_text += '📌 /acmp \\- панель управления Acmp  \n'
        help_text += '📌 /sheets \\- панель управления Google Sheets \\(Журнал\\)  \n'
        await message.answer(help_text, parse_mode='MarkdownV2')
        
    # Request accept command handler
    async def accept_verification_request(self, message: types.Message):
        # User is admin or owner
        if (message.from_id != config.owner):
            if (not check_role(message, ['admin'])):
                return
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
        user = Cache.get_user(request[0])
        user.del_request()
        user.set_role('teacher')
        await self.bot.send_message(request[0], 'Ваша заявка рассмотрена! Вы получили доступ к основным функциям бота /help')
        await message.answer('Done')

def setup(dp: Dispatcher, bot):
    OwnerModule(dp, bot)