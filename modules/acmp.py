from config import config
from aiogram import Bot, Dispatcher, types

from modules.utils.user import BotUser, Group

from .utils.db import PostgresDatabase
from .utils.cache import Cache

from .elements.keyboards import AcmpInlineKeyboard

from .utils.acmp import AcmpParser

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from .utils.markdown_escape import escape
from .utils.sheets.sheets import GradesSheet, Table

import re

class SelectTaskForm(StatesGroup):
    task_id = State()

class AcmpModule():
    def __init__(self, dp: Dispatcher, bot: Bot):
        self.dp = dp
        self.bot = bot
        
        self.group_cache = {}
        
        dp.register_callback_query_handler(self.on_acmp_menu_clicked, lambda c: c.data.startswith("groups_acmp_"), role=['teacher', 'admin'])
        dp.register_callback_query_handler(self.on_acmp_review_one_clicked, lambda c: c.data.startswith("acmp_review_one_"), role=['teacher', 'admin'])
        
        dp.register_message_handler(self.on_assignment_index_received, state=SelectTaskForm.task_id)
    
    async def on_acmp_menu_clicked(self, callback_query: types.CallbackQuery):
        print('on_acmp_menu_clicked')
        await self.bot.answer_callback_query(callback_query.id)
        
        group_index = int(callback_query.data.split('_')[-1])
        user = Cache.get_user(callback_query.from_user.id)
        group = user.groups[group_index]
        
        answer = ''
        answer += f'⚡ *{group.name}*\n'
        answer += 'Выберите действие\\:'
        
        await callback_query.message.edit_text(answer, parse_mode="MarkdownV2", reply_markup=AcmpInlineKeyboard(group_index))
        
    async def on_acmp_review_one_clicked(self, callback_query: types.CallbackQuery):
        print('on_acmp_review_one_clicked')
        await self.bot.answer_callback_query(callback_query.id)
        
        group_index = int(callback_query.data.split('_')[-1])
        user = Cache.get_user(callback_query.from_user.id)
        group = user.groups[group_index]
        
        self.group_cache[user.id] = group_index
        
        await callback_query.message.answer('Введите номер задачи:')
        await SelectTaskForm.task_id.set()
        
    async def on_assignment_index_received(self, message: types.Message, state: FSMContext):
        if (re.match(r"\d+", message.text)):
            task_id = int(message.text)
            user = Cache.get_user(message.from_id)
            if (1 <= task_id <= 1000):
                progress_message = await message.answer('Начинаю проверку, это займет некоторое время...')
                await self.review_task(task_id, user)
                await progress_message.edit_text('Выполнено!')
                await state.finish()
                await self.send_acmp_menu(user)
                return
        await message.answer('Такой задачи нет. Попробуйте еще раз')
    
    async def send_acmp_menu(self, user):
        user: BotUser
        group_index = self.group_cache[user.id]
        group = user.groups[group_index]
        
        answer = ''
        answer += f'⚡ *{group.name}*\n'
        answer += 'Выберите действие\\:'
        
        await self.bot.send_message(user.id, answer, parse_mode="MarkdownV2", reply_markup=AcmpInlineKeyboard(group_index))

    
    async def review_task(self, id: int, user: BotUser):
        group_index = self.group_cache[user.id]
        group: Group = user.groups[group_index]
        gsheets = GradesSheet(group.sheets)
        table = gsheets.get_acmp_table()
        children = []
        for i in table.get_logins_list():
            if (i != ''):
                children.append(i)
        parser = AcmpParser(children)
        solvers = parser.get_solvers(id)
        table.set_grade(id, solvers)

def setup(dp: Dispatcher, bot):
    AcmpModule(dp, bot)