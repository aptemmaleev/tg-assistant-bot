from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ..utils.user import User, Group

# Start verification
start_verification_button = InlineKeyboardButton(text='Начать верификацию',
                                                 callback_data='start_verification_button')
start_verification_keyboard = InlineKeyboardMarkup()
start_verification_keyboard.add(start_verification_button)

# Groups Inline Keyboard
class GroupsInlineKeyboard(InlineKeyboardMarkup):
    """**GroupsInlineKeyboard**
    
    Groups keyboard
    
    Group button callback_data:
        "groups_select_{group_index}"
    
    Add group button callback_data:
        "groups_add"
    """
    def __init__(self, user: User, row_width=1):
        super().__init__(row_width)
        if (len(user.groups) != 0):
            for i in range(len(user.groups)):
                self.add(InlineKeyboardButton(user.groups[i].name, callback_data=f'groups_select_{i}'))
        self.add(InlineKeyboardButton('Добавить', callback_data=f'groups_add'))

# Add Google Sheets Inline Keyboard
class AddGoogleSheetsInlineKeyboard(InlineKeyboardMarkup):
    """AddGoogleSheetsInlineKeyboard

    callback_data:
        "groups_add_sheets"
    """
    def __init__(self, row_width=1):
        super().__init__(row_width)
        self.add(InlineKeyboardButton('Далее', callback_data=f'groups_add_sheets'))
        
# Select group inline keyboard
class SelectedGroupInlineKeyboard(InlineKeyboardMarkup):
    """SelectedGroupInlineKeyboard

    callback_data:
        "groups_delete_{group_index}"
    """
    def __init__(self, group_index, row_width=1):
        super().__init__(row_width)
        self.add(InlineKeyboardButton('OnlineGDB', callback_data=f'groups_onlinegdb_{group_index}'))
        self.add(InlineKeyboardButton('ACMP', callback_data=f'groups_acmp_{group_index}'))
        self.add(InlineKeyboardButton('Назад', callback_data=f'return_to_groups'))

# OnlineGDB Menu
class OnlineGdbInlineKeyboard(InlineKeyboardMarkup):
    """OnlineGdbInlineKeyboard

    callback_data:
        "onlinegdb_{group_index}"
    """
    def __init__(self, group_index, row_width=1):
        super().__init__(row_width)
        self.add(InlineKeyboardButton('Проверить задачу', callback_data=f'onlinegdb_review_one_{group_index}'))
        self.add(InlineKeyboardButton('Выставить оценки', callback_data=f'onlinegdb_grade_one_{group_index}'))
        self.add(InlineKeyboardButton('Проверить все', callback_data=f'onlinegdb_review_all_{group_index}'))
        self.add(InlineKeyboardButton('Выставить все', callback_data=f'onlinegdb_grade_all_{group_index}'))
        self.add(InlineKeyboardButton('Назад', callback_data=f'return_to_groups'))


# Acmp Menu
class AcmpInlineKeyboard(InlineKeyboardMarkup):
    """AcmpInlineKeyboard

    callback_data:
        "onlinegdb_{group_index}"
    """
    def __init__(self, group_index, row_width=1):
        super().__init__(row_width)
        self.add(InlineKeyboardButton('Выгрузить выполнивших', callback_data=f'acmp_review_one_{group_index}'))
        self.add(InlineKeyboardButton('Назад', callback_data=f'return_to_groups'))