import os
from dotenv import load_dotenv
from telebot import TeleBot

from .handlers.main import *

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

def register_handlers():
    bot.register_message_handler(commands_handler, commands=['start', 'month_list', 'list', 'add', 'remove', 'remove_all','table_init', 'id', 'upload_table'], pass_bot=True)
