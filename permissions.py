from typing import Union
from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

class TeacherFilter(BoundFilter):
    key = 'is_teacher'
    
    def __init__(self, is_teacher: bool):
        self.teachers = [1234, 11111]
        self.is_teacher = is_teacher
    
    async def check(self, obj: Union[types.Message, types.CallbackQuery]):
        user = obj.from_user
        if (user.id in self.teachers):
            return self.is_teacher is True
        else:
            return self.is_teacher is False
