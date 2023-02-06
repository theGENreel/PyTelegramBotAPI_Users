import json
from os.path import exists, join
from os import getcwd

from aiofiles import open
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


class AsyncTeleBotUsers:
    def __init__(self, bot: AsyncTeleBot, admin_chat_id: int|str, files_dir=getcwd()):
        self.requests = {}
        self.users = {}
        self.bot = bot
        self.admin_chat_id = str(admin_chat_id)
        self.files_dir = files_dir
        self.requests_path = join(self.files_dir, 'requests.json')
        self.users_path = join(self.files_dir, 'users.json')

    async def save_requests(self):
        async with open(self.requests_path, 'w') as file:
            text = json.dumps(self.requests)
            await file.write(text)

    async def load_requests(self):
        async with open(self.requests_path, 'r') as file:
            text = await file.read()
            self.requests = json.loads(text)

    async def save_users(self):
        async with open(self.users_path, 'w') as file:
            text = json.dumps(self.users)
            await file.write(text)

    async def load_users(self):
        async with open(self.users_path, 'r') as file:
            text = await file.read()
            self.users = json.loads(text)

    async def init(self):
        if exists(self.requests_path):
            await self.load_requests()
        else:
            await self.save_requests()
        if exists(self.users_path):
            await self.load_users()
        else:
            await self.save_users()

        self.bot.register_message_handler(self.request_handler, commands=['start', 'request'])
        self.bot.register_message_handler(self.manage_requests_handler, commands=['manage_requests'])
        self.bot.register_message_handler(self.manage_users_handler, commands=['manage_users'])
        self.bot.register_callback_query_handler(self.query_handler, func=lambda call: True)

    async def add_request(self, chatid, title: str = None, first_name: str = None, username: str = None, last_name: str = None):
        chatid = str(chatid)
        if title is not None:
            self.requests[chatid] = {'name': title, 'type': 'group'}
        else:
            self.requests[chatid] = {'name': f'{str(first_name)} {str(last_name)}\n{str(username)}', 'type': 'private'}
        await self.save_requests()

    async def remove_request(self, chatid):
        chatid = str(chatid)
        del self.requests[chatid]
        await self.save_requests()

    async def add_user(self, chatid):
        chatid = str(chatid)
        self.users[chatid] = self.requests[chatid]
        del self.requests[chatid]
        await self.save_users()
        await self.save_requests()

    async def remove_user(self, chatid):
        chatid = str(chatid)
        del self.users[chatid]
        await self.save_users()

    async def write_attribute(self, chatid, name, value):
        chatid = str(chatid)
        if chatid in self.users and name != 'name' and name != 'type':
            self.users[chatid][name] = value
        await self.save_users()

    async def read_attribute(self, chatid, name):
        chatid = str(chatid)
        if chatid in self.users:
            if name in self.users[chatid]:
                return self.users[chatid][name]
        return None

    async def delete_attribute(self, chatid, name):
        chatid = str(chatid)
        if chatid in self.users:
            if name in self.users[chatid]:
                del self.users[chatid][name]
        await self.save_users()

    async def request_handler(self, message):
        message.chat.id = str(message.chat.id)
        if message.chat.type == 'group':
            await self.add_request(message.chat.id, title=message.chat.title)
            await self.bot.reply_to(message, 'Request sended. Now wait for admin to approve your request.')
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(InlineKeyboardButton('Remove', callback_data=f'remove_request,{message.chat.id}'),
                       InlineKeyboardButton('Add', callback_data=f'add_user,{message.chat.id}'))
            await self.bot.send_message(self.admin_chat_id,
                                        f'New request!\n\n{self.requests[message.chat.id]["type"]}\n{self.requests[message.chat.id]["name"]}',
                                        reply_markup=markup)
        elif message.chat.type == 'private':
            await self.add_request(message.chat.id, first_name=message.from_user.first_name, last_name=message.from_user.last_name,
                        username=message.from_user.username)
            await self.bot.reply_to(message, 'Request sended. Now wait for admin to approve your request.')
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(InlineKeyboardButton('Remove', callback_data=f'remove_request,{message.chat.id}'),
                       InlineKeyboardButton('Add', callback_data=f'add_user,{message.chat.id}'))
            await self.bot.send_message(self.admin_chat_id,
                                        f'New request!\n\n{self.requests[message.chat.id]["type"]}\n{self.requests[message.chat.id]["name"]}',
                                        reply_markup=markup)

    async def manage_requests_handler(self, message):
        message.chat.id = str(message.chat.id)
        if message.chat.id == self.admin_chat_id:
            for request in self.requests:
                markup = InlineKeyboardMarkup()
                markup.row_width = 1
                markup.add(InlineKeyboardButton('Remove', callback_data=f'remove_request,{request}'),
                           InlineKeyboardButton('Add', callback_data=f'add_user,{request}'))
                await self.bot.send_message(self.admin_chat_id,
                                            f"{self.requests[request]['type']}\n{self.requests[request]['name']}",
                                            reply_markup=markup)

    async def manage_users_handler(self, message):
        message.chat.id = str(message.chat.id)
        if message.chat.id == self.admin_chat_id:
            for user in self.users:
                markup = InlineKeyboardMarkup()
                markup.row_width = 1
                markup.add(InlineKeyboardButton('Remove', callback_data=f'remove_user,{user}'))
                await self.bot.send_message(self.admin_chat_id, f'{self.users[user]["type"]}{self.users[user]["name"]}',
                                            reply_markup=markup)

    async def query_handler(self, call):
        call.message.chat.id = str(call.message.chat.id)
        if call.message.chat.id == self.admin_chat_id:
            action = call.data.split(',')[0]
            value = call.data.split(',')[1]
            if action == 'remove_request':
                await self.remove_request(value)
                await self.bot.answer_callback_query(call.id, f'Request {value} removed')
                await self.bot.delete_message(call.message.chat.id, call.message.id)
            elif action == 'add_user':
                await self.add_user(value)
                await self.bot.answer_callback_query(call.id, f'User {value} added')
                await self.bot.delete_message(call.message.chat.id, call.message.id)
                await self.bot.send_message(value, 'The admin has confirmed your request')
            elif action == 'remove_user':
                await self.remove_user(value)
                await self.bot.answer_callback_query(call.id, f'User {value} removed')
                await self.bot.delete_message(call.message.chat.id, call.message.id)
                await self.bot.send_message(value, 'The admin has revoke your access')
