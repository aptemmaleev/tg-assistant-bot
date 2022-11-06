from config import config
from utils.db import PostgresDatabase
from aiogram import Bot, Dispatcher, executor, types

# Initialize
PostgresDatabase(host=config.database.host,
                 port=config.database.port,
                 database=config.database.database,
                 user=config.database.user,
                 password=config.database.password)

bot = Bot(token=config.token)
dp = Dispatcher(bot)

# Start command handler
@dp.message_handler(commands=["start", "help"])
async def welcome_message(message: types.Message):
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
    await message.answer(answer, parse_mode="MarkdownV2")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)