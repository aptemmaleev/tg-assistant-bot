from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Start verification
start_verification_button = InlineKeyboardButton(text='Начать верификацию',
                                                 callback_data='start_verification_button')
start_verification_keyboard = InlineKeyboardMarkup()
start_verification_keyboard.add(start_verification_button)