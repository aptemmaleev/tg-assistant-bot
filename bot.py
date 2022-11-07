import os
import importlib

from aiogram import Bot, Dispatcher, executor

from config import config
from utils.db import PostgresDatabase
from utils.cache import Cache
from filters.role import setup_permissions

# Initialize database
PostgresDatabase(host=config.database.host,
                 port=config.database.port,
                 database=config.database.database,
                 user=config.database.user,
                 password=config.database.password)

# Initialize caching
Cache()

# Initialize telegram bot
bot = Bot(token=config.token)
dp = Dispatcher(bot)

# Initialize filters
setup_permissions(dp)

# Loading modules
tree = os.listdir('modules')
for module in tree:
    if (module.endswith('.py')):
        path = 'modules.' + module[:-3]
        mod = importlib.import_module(path)
        mod.setup(dp, bot)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)