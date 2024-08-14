import os
from dotenv import load_dotenv
from telebot import TeleBot

from .handlers.main import *

#TODO: переписать логику отправки поздравлений так чтобы алгоритм сверялся с датой ежедневно

def start_bot():
    load_dotenv()
    global bot
    bot = init_bot()
    register_handlers()
    bot.infinity_polling(timeout=5)

# Включение бота
def init_bot():
    TOKEN = os.getenv('API_KEY')
    bot = TeleBot(TOKEN)
    return bot

# Узнать ID чата и топика
def print_id(message, bot):
    if str(message.from_user.id) not in admins_id: return
    chat_id = message.chat.id
    try: msg_thread_id = message.reply_to_message.message_thread_id
    except AttributeError: msg_thread_id = "General"
    print(f"Chat ID этого чата: {chat_id}\nИ message_thread_id: {msg_thread_id}")

def register_handlers():
    bot.register_message_handler(commands_handler_admin, commands=['start', 'month_list', 'list', 'add', 'remove', 'remove_all','table_init'], pass_bot=True)
    bot.register_message_handler(print_id, commands=['id'], pass_bot=True)
