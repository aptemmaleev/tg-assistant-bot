from random import randint
from config import config
from aiogram import Bot, Dispatcher, types

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from .elements.keyboards import GroupsInlineKeyboard, AddGoogleSheetsInlineKeyboard, SelectedGroupInlineKeyboard

from .utils.cache import Cache
from .utils.user import User, Group

from filters.permissions import check_role

from .utils.sheets.sheets import GradesSheet, Table

from typing import List

import re

class NewGroupForm(StatesGroup):
    sheets_url = State()
    name = State()

class GroupModule():
    def __init__(self, dp: Dispatcher, bot: Bot):
        self.dp = dp
        self.bot = bot
        
        self.user_sheets = {}
        
        dp.register_message_handler(self.groups_command, commands=["groups", "группы"], role=['teacher', 'admin'])
        
        dp.register_callback_query_handler(self.on_select_group_button_clicked, lambda c: c.data.startswith("groups_select_"), role=['teacher', 'admin'])
        dp.register_callback_query_handler(self.on_add_group_button_clicked, lambda c: c.data == "groups_add", role=['teacher', 'admin'])
        dp.register_callback_query_handler(self.on_add_google_sheets_button_clicked, lambda c: c.data == "groups_add_sheets", role=['teacher', 'admin'])

        dp.register_callback_query_handler(self.on_return_to_groups_clicked, lambda c: c.data == "return_to_groups", role=['teacher', 'admin'])
        
        dp.register_message_handler(self.on_sheets_url_received, state=NewGroupForm.sheets_url)
        dp.register_message_handler(self.on_sheets_name_received, state=NewGroupForm.name)
    
    async def groups_command(self, message: types.Message):
        print('groups_command')
        
        user = Cache.get_user(message.from_id)
        answer = '📕*Список ваших групп:* \n'
        if (len(user.groups) != 0):
            for group in user.groups:
                group: Group = group
                answer += f'⚡ {group.name}\n'
        else:
            answer = '*Список пуст, добавьте новую группу* \n'
        await message.answer(answer, parse_mode="MarkdownV2", reply_markup=GroupsInlineKeyboard(user))
        
    async def on_add_group_button_clicked(self, callback_query: types.CallbackQuery):
        print('on_add_group_button_clicked')
        # Answer callback
        await self.bot.answer_callback_query(callback_query.id)
        # Get user
        user = Cache.get_user(callback_query.from_user.id)
        
        # Answer
        answer = f'*⚠ Важно\\!*\n'
        answer += f'Перед тем как создать новую группу\\, необходимо добавить сервисный аккаунт гугл редактором в ваш журнал\\. '
        answer += f'Для этого на вкладке таблицы нужно нажать на кнопку *Настройки доступа* и в поле *Добавьте пользователей или группы* '
        answer += f'введите адрес `autosheets@cshelper-366120.iam.gserviceaccount.com` \\(нажмите, чтобы скопировать\\)\\. Убедитесь\\, '
        answer += f'что предоставлен уровень доступа *Редактор* и после нажмите на кнопку *Отправить*\\.\n\n'
        answer += f'👆 После выполнения действий сверху нажмите на кнопку *Далее* и укажите ссылку на ваш журнал в Google Sheets\\.\n'

        await callback_query.message.edit_text(answer, parse_mode="MarkdownV2", reply_markup=AddGoogleSheetsInlineKeyboard())
    
    async def on_add_google_sheets_button_clicked(self, callback_query: types.CallbackQuery):
        print('on_add_group_button_clicked')
        # Answer callback
        await self.bot.answer_callback_query(callback_query.id)
        # Get user
        user = Cache.get_user(callback_query.from_user.id)
        # Answer
        await NewGroupForm.sheets_url.set()
        answer = '**Пришлите ссылку на ваш журнал**'
        await callback_query.message.edit_text(answer, parse_mode="MarkdownV2")
        
    async def on_return_to_groups_clicked(self, callback_query: types.CallbackQuery):
        print('on_return_to_groups_clicked')
        # Answer callback
        await self.bot.answer_callback_query(callback_query.id)
        # Get user
        user = Cache.get_user(callback_query.from_user.id)
        answer = '📕*Список ваших групп:* \n'
        if (len(user.groups) != 0):
            for group in user.groups:
                group: Group = group
                answer += f'⚡ {group.name}\n'
        else:
            answer = '*Список пуст, добавьте новую группу* \n'
        await callback_query.message.edit_text(answer, parse_mode="MarkdownV2", reply_markup=GroupsInlineKeyboard(user))
        
    async def on_sheets_url_received(self, message: types.Message, state: FSMContext):
        url = message.text
        if (url.find('docs.google.com/spreadsheets/d/')):
            url = url.split('/')
            sheets_id = ''
            for i in range(len(url)):
                if (url[i] == 'd'):
                    sheets_id = url[i + 1]
            print(sheets_id)
            try:
                sheets = GradesSheet(sheets_id)
                answer = f'Отлично\\! У меня есть доступ к этому журналу\\!\nТеперь укажите название группы \\(не больше 32 символов\\)\\:'
                await NewGroupForm.name.set()
                self.user_sheets[message.from_id] = sheets_id
                await message.answer(answer, parse_mode="MarkdownV2")
            except Exception as e:
                await message.answer(f'Error: {e}')
    
    async def on_sheets_name_received(self, message: types.Message, state: FSMContext):
        name = message.text
        if (re.match(r"[a-zA-Z ]{3,32}", message.text)):
            user = Cache.get_user(str(message.from_id))
            user.add_group(name, self.user_sheets[message.from_id])
            # user = Cache.update_user(user.id)
            await message.answer(f'Группа {name} успешно добавлена! Список доступных групп: /groups')
            await state.finish()
            return
        message.answer('Неправильный формат имени (длина от 3 до 32 символов, английские буквы и пробел)')
    
    async def on_select_group_button_clicked(self, callback_query: types.CallbackQuery):
        print('on_select_group_button_clicked')
        # Answer callback
        await self.bot.answer_callback_query(callback_query.id)
        
        # Getting group
        user = Cache.get_user(callback_query.from_user.id)
        group_index = int(callback_query.data.split('_')[-1])
        group: Group = user.groups[group_index]
        
        # Answer
        answer = f'**⚡ {group.name}**\n'
        answer += f'✅ Журнал: *Подключен*\n' if group.sheets != None else f'❎ Журнал: *Не подключен*\n'
        answer += f'✅ OnlineGDB: *Подключен*\n' if group.gdb != None else f'❎ OnlineGDB: *Не подключен*\n'
        answer += f'✅ ACMP: *Подключен*\n' if group.acmp == True else f'❎ ACMP: *Не подключен*\n'
        
        await callback_query.message.edit_text(answer, parse_mode="MarkdownV2", reply_markup=SelectedGroupInlineKeyboard(group_index))
                
    async def cancel_handler(self, message: types.Message, state: FSMContext):
        """
        Allow user to cancel any action
        """
        current_state = await state.get_state()
        if current_state is None:
            return

        print('Cancelling state %r', current_state)
        # Cancel state and inform user about it
        await state.finish()
        # And remove keyboard (just in case)
        await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())
    
        
def setup(dp: Dispatcher, bot):
    GroupModule(dp, bot)