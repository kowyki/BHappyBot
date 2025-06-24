import os
from dotenv import load_dotenv
from telebot import TeleBot

from .handlers.main import *

def start_bot():
    load_dotenv()
    global bot
    bot = init_bot()
    register_handlers()
    start_services(bot)
    bot.infinity_polling(timeout=5)

# Включение бота
def init_bot():
    TOKEN = os.getenv('API_KEY')
    bot = TeleBot(TOKEN)
    return bot

def register_handlers():
    bot.register_message_handler(commands_handler, commands=['start', 'list', 'add', 'remove', 'clear', 'timer', 'add_google_sheets', 'table_sync', 'id', 'info'], pass_bot=True)

# Действия после включения бота
def start_services(bot: TeleBot):
    data_path = os.path.dirname(os.path.realpath(__file__))
    data_path = data_path[:data_path.index('bot')]
    data_path = os.path.join(data_path, 'data', 'data.db')
    if not os.path.isfile(data_path):
        create_db()

    start_timer(bot)
