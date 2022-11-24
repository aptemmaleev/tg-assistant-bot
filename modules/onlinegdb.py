import asyncio
from random import randint
from config import config
from aiogram import Bot, Dispatcher, types

from .utils.cache import Cache
from .utils.user import BotUser, Group
from .utils.db import PostgresDatabase
from .elements.keyboards import OnlineGdbInlineKeyboard, start_verification_keyboard

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from .utils.onlinegdb import AutoOnlinegdb, Assignment

from filters.permissions import check_role

from .utils.markdown_escape import escape
from .utils.sheets.sheets import GradesSheet, Table

import re

class SelectAssignmentForm(StatesGroup):
    assignment_index = State()

class OnlineGdbModule():
    def __init__(self, dp: Dispatcher, bot: Bot):
        self.dp = dp
        self.bot = bot
        self.assignments_cache = {}
        self.action_cache = {}
        
        dp.register_callback_query_handler(self.on_onlinegdb_button_clicked, lambda c: c.data.startswith("groups_onlinegdb_"), role=['teacher', 'admin'])
        
        dp.register_callback_query_handler(self.on_review_one_clicked, lambda c: c.data.startswith("onlinegdb_review_one_"), role=['teacher', 'admin'])
        dp.register_callback_query_handler(self.on_grade_one_clicked, lambda c: c.data.startswith("onlinegdb_grade_one_"), role=['teacher', 'admin'])
        dp.register_callback_query_handler(self.on_review_all_clicked, lambda c: c.data.startswith("onlinegdb_review_all_"), role=['teacher', 'admin'])
        dp.register_callback_query_handler(self.on_grade_all_clicked, lambda c: c.data.startswith("onlinegdb_grade_all"), role=['teacher', 'admin'])
        
        dp.register_message_handler(self.on_assignment_index_received, state=SelectAssignmentForm.assignment_index)
        
    async def on_review_one_clicked(self, callback_query: types.CallbackQuery):
        print('on_review_one_clicked')
        group_index = int(callback_query.data.split('_')[-1])
        await self.bot.answer_callback_query(callback_query.id)
        self.action_cache[callback_query.from_user.id] = (group_index, 'review_one')
        await callback_query.message.answer('Введите номер задачи:')
        await SelectAssignmentForm.assignment_index.set()
        
    async def on_grade_one_clicked(self, callback_query: types.CallbackQuery):
        print('on_grade_one_clicked')
        group_index = int(callback_query.data.split('_')[-1])
        await self.bot.answer_callback_query(callback_query.id)
        self.action_cache[callback_query.from_user.id] = (group_index, 'grade_one')
        await callback_query.message.answer('Введите номер задачи:')
        await SelectAssignmentForm.assignment_index.set()
        
    async def on_review_all_clicked(self, callback_query: types.CallbackQuery):
        print('on_review_all_clicked')
        # Answer callback
        await self.bot.answer_callback_query(callback_query.id)
        
        group_index = int(callback_query.data.split('_')[-1])
        user: BotUser = Cache.get_user(callback_query.from_user.id)
        group = user.groups[group_index]
        
        agdb = AutoOnlinegdb(group.gdb)
        assignments_list = agdb.get_assignments()
        
        progress_message = await callback_query.message.answer('Начинаю проверку!')
        
        k = 0
        for i in range(len(assignments_list)):
            if (k > 4):
                await progress_message.edit_text(f'Проверено: {i}/{len(assignments_list)}')
                k = 0
            else:
                k += 1
            assignment: Assignment = assignments_list[i]
            if (assignment.pending_count > 0):
                assignment.review()
        
        await progress_message.edit_text(f'*Все задачи проверенны\\!*', parse_mode="MarkdownV2")
        await asyncio.sleep(5)
        await progress_message.delete()
        
    async def on_grade_all_clicked(self, callback_query: types.CallbackQuery):
        print('on_grade_all_clicked')
        # Answer callback
        await self.bot.answer_callback_query(callback_query.id)
        
        group_index = int(callback_query.data.split('_')[-1])
        user: BotUser = Cache.get_user(callback_query.from_user.id)
        group = user.groups[group_index]
        table = GradesSheet(group.sheets).get_onlinegdb_table()

        agdb = AutoOnlinegdb(group.gdb)
        assignments_list = agdb.get_assignments()
        
        progress_message = await callback_query.message.answer('Начинаю выставлять задачи!')
        
        k = 0
        for i in range(len(assignments_list)):
            assignment: Assignment = assignments_list[i]
            if (assignment.get_active_status()):
                print(f'Пропустил: {assignment.name}')
                continue
            assignment.update_done()
            print(f'Сейчас выставляю: {assignment.name}')
            if (k > 4):
                await progress_message.edit_text(f'Выставлено: {i}/{len(assignments_list)}')
                k = 0
            else:
                k += 1
            table.set_grade(assignment.id, assignment.done, assignment.name)
            await asyncio.sleep(1)
        await progress_message.edit_text(f'*Все оценки выставлены\\!*', parse_mode="MarkdownV2")
        await asyncio.sleep(5)
        await progress_message.delete()
                 
    
    async def on_onlinegdb_button_clicked(self, callback_query: types.CallbackQuery):
        print('on_onlinegdb_button_clicked')
        # Answer callback
        await self.bot.answer_callback_query(callback_query.id)
        
        # Getting group
        user = Cache.get_user(callback_query.from_user.id)
        group_index = int(callback_query.data.split('_')[-1])
        group: Group = user.groups[group_index]
        
        # Get Assignments List
        agdb = AutoOnlinegdb(group.gdb)
        assignments_list = agdb.get_assignments()
        self.assignments_cache[user.id] = assignments_list

        # Build answer
        answer = f'⚡*{group.name}*\n'
        k = 0
        for assignment in assignments_list:
            assignment: Assignment
            answer += f'*\\({k}\\)* {escape(assignment.name)} \\[{assignment.not_submitted_count}\\/{assignment.pending_count}\\/{assignment.done_count}\\]\n'
            k += 1
        
        await callback_query.message.edit_text(answer, parse_mode="MarkdownV2", reply_markup=OnlineGdbInlineKeyboard(group_index))
    
    async def on_assignment_index_received(self, message: types.Message, state: FSMContext):
        if (re.match(r"\d+", message.text)):
            index = int(message.text)
            user = Cache.get_user(message.from_id)
            action = self.action_cache[user.id]
            if (0 <= index <= len(self.assignments_cache[user.id])):
                if (action[1] == 'review_one'):
                    await self.review_one(message, index)
                elif (action[1] == 'grade_one'):
                    await self.grade_one(message, index)
                await state.finish()
                return
        await message.answer('Такой задачи нет. Попробуйте еще раз')
    
    async def send_onlinegdb_menu(self, message: types.Message, group):
        # Getting group
        user = Cache.get_user(message.from_id)
        group_index = int(group)
        group: Group = user.groups[group_index]
        
        # Get Assignments List
        agdb = AutoOnlinegdb(group.gdb)
        assignments_list = agdb.get_assignments()
        self.assignments_cache[user.id] = assignments_list

        # Build answer
        answer = f'⚡*{group.name}*\n'
        k = 0
        for assignment in assignments_list:
            assignment: Assignment
            answer += f'*\\({k}\\)* {escape(assignment.name)} \\[{assignment.not_submitted_count}\\/{assignment.pending_count}\\/{assignment.done_count}\\]\n'
            k += 1
        
        await message.answer(answer, parse_mode="MarkdownV2", reply_markup=OnlineGdbInlineKeyboard(group_index))
    
    async def review_one(self, message: types.Message, index):
        assignment: Assignment = self.assignments_cache[message.from_id][index]
        done_count = assignment.done_count
        done = assignment.done
        assignment.review()
        assignment.update_done()
        new_done = list(set(assignment.done) - set(done))
        answer = f'Задача *{escape(assignment.name)}* проверена\\!\n'
        answer += f'Количество выполнивших: {assignment.done_count} \\(было: {done_count}\\)\n'
        if (len(new_done)):
            answer += f'Новые выполнившие\\:\n'
            for child in new_done:
                answer += f'{child}\n'
        await message.answer(answer, parse_mode="MarkdownV2")
        await self.send_onlinegdb_menu(message, self.action_cache[message.from_id][0])
    
    async def grade_one(self, message, index):
        user: BotUser = Cache.get_user(message.from_id)
        action = self.action_cache[message.from_id]
        group: Group = user.groups[action[0]]
        
        table = GradesSheet(group.sheets).get_onlinegdb_table()
        
        assignment: Assignment = self.assignments_cache[user.id][index]
        assignment.update_done()
        table.set_grade(assignment.id, assignment.done, assignment.name)
        await message.answer(f'Оценки за задачу {escape(assignment.name)} выставлены\\!', parse_mode="MarkdownV2")
        await self.send_onlinegdb_menu(message, self.action_cache[message.from_id][0])
        
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