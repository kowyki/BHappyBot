from os import path, getenv
from dotenv import load_dotenv
from telebot import TeleBot

from .handlers.main import commands_handler, adding_to_chat_handler, removing_from_chat_handler
from .handlers.keyboard import keyboard_handler
from .data.main_data import create_db

def start_bot():
    load_dotenv()
    global bot
    bot = init_bot()

    register_handlers()
    start_services()
    bot.infinity_polling(timeout=5)

# Включение бота
def init_bot():
    TOKEN = getenv('API_KEY')

    bot = TeleBot(TOKEN)
    return bot

def register_handlers():
    bot.register_message_handler(commands_handler, commands=['start', 'list', 'add', 'remove', 'clear', 'timer', 'add_google_sheets', 'table_sync', 'id', 'info'], pass_bot=True)
    bot.register_message_handler(adding_to_chat_handler, content_types=['new_chat_members'], pass_bot=True)
    bot.register_message_handler(removing_from_chat_handler, content_types=['left_chat_member'], pass_bot=True)
    bot.register_message_handler(keyboard_handler, content_types=['text'], pass_bot=True)


# Действия после включения бота
def start_services():
    data_path = path.dirname(path.realpath(__file__))
    data_path = path.join(data_path, 'data', 'data.db')
    if not path.isfile(data_path):
        create_db()

