# PyTelegramBotAPI_Users
User access manager for <a href='https://github.com/eternnoir/pyTelegramBotAPI'>pyTelegramBotAPI</a>. For now async only.

## Features
 - Send access requests to admin
 - Send a message to the administrator upon receipt of a new request
 - Manage requests and users
 - Store additional attributes for each user separately

## Installation

* Installation from source (requires git):

```
$ git clone https://github.com/theGENreel/PyTelegramBotAPI_Users.git
$ cd PyTelegramBotAPI_Users
$ python setup.py install
```
or:
```
$ pip install git+https://github.com/theGENreel/PyTelegramBotAPI_Users.git
```
## Quick start
```python
import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot_users.async_users import AsyncTeleBotUsers

async def main():
    bot = AsyncTeleBot(TOKEN)
    bot_users = AsyncTeleBotUsers(bot, ADMIN_CHATID)
    
    await bot_users.init()
    await bot.polling()
    
asyncio.run(main())
```
## Usage
Create an instance of AsyncTeleBotUsers class. Pass a AsyncTeleBot instance, admin chat_id and optionaly path to folder where to store requests.json and users.json.
```python
bot_users = AsyncTeleBotUsers(bot, ADMIN_CHATID, PATH_TO_FILES)
```
Await bot_users.init() before bot.polling().
```python
await bot_users.init()
await bot.polling()
```
In message handlers use bot_users.users to check if user have access to bot.
```python
@bot.message_handler(commands=['work'])
async def work(message):
    if message.chat.id in bot_users.users:
        # Do some work
```
