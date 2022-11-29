# Assistant Bot

```
🔱 Developer: Aptem M
🎮 Discord: Aptem#9434
✉️ Telegram: @aptemm
```

## Экономлю ваше время

Телеграмм бот на основе библиотеки aiogram для автоматизации проверок 
практических работ слушателей курсов Школы::Кода по Python.

- Автоматизация [OnlineGDB Classroom]
- Парсинг решений с [ACMP]
- Парсинг решений с [Codeforces] (в планах)

## Техническая часть

Assistant Bot использует ряд проектов с открытым исходным кодом для работы:
- [aiogram] - Simple and fully asynchronous framework for Telegram Bot API
- [gspread] - Google Sheets Python API
- [BeautifulSoup4] - Pulling data out of HTML and XML file
- [Random User-Agent] - Automatically replaces the User-Agent with a randomized one.
- [pdoc] - API Documentation for Python Projects
- [psycopg2] - PostgreSQL database adapter for the Python programming language

## Установка

Склонируйте репозиторий и настройте файл конфигурации:

```json
{
    "token": "telegram_bot_token",
    "database": {
        "host": "postgres",
        "port": "postgres",
        "database": "postgres",
        "user": "postgres",
        "password": "postgres"
    },
    "onlinegdb": {
        "email": "",
        "password": ""
    },
    "owner": 11111
}
```

Поместите в папку `\data` сервисный аккаунт гугл `service_account.json`.
И после запустите бота с помощью команды терминала:
```sh
python bot.py
```

## License

MIT

**Free Software, Hell Yeah!**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [OnlineGDB Classroom]: <https://www.onlinegdb.com/classroom>
   [ACMP]: <https://acmp.ru/>
   [Codeforces]: <https://codeforces.com/>
   [BeautifulSoup4]: <https://github.com/wention/BeautifulSoup4>
   [Random User-Agent]: <https://github.com/tarampampam/random-user-agent>
   [aiogram]: <https://github.com/aiogram/aiogram>
   [gspread]: <https://github.com/burnash/gspread>
   [pdoc]: <https://github.com/mitmproxy/pdoc>
   [psycopg2]: <https://github.com/psycopg/psycopg2>
