import sqlite3
from telebot import TeleBot
from telebot.types import Message

from ..classes import *
from ..keyboards.reply import choose_chat_kb

def modify_chats_markup(admin_id: int):
    db = sqlite3.connect('bot/data/data.db')
    cursor = db.cursor()
    cursor.execute(f'SELECT chat_title FROM admins WHERE admin_id = ?', [admin_id])
    chat_data = [data[0] for data in cursor.fetchall()] + ['Добавить чат']
    db.close()

    return choose_chat_kb(chat_data)

# Узнать ID чата и топика
def print_id(message: Message, bot: TeleBot) -> None:
    if message.chat.type == "private": 
        bot.send_message(message.from_user.id, f"Напишите команду /id в топик, в который хотите чтобы бот присылал поздравления")
    else:
        chat_id = Chat_ID(message.chat.id)
        try: thread_id = message.reply_to_message.message_thread_id
        except AttributeError: thread_id = "General"

        try: 
            db = sqlite3.connect('bot/data/data.db')
            cursor = db.cursor()
            cursor.execute(f'UPDATE admins SET thread_id = ? WHERE chat_id = ?', [thread_id, chat_id.integer])
            db.commit()
            bot.send_message(message.from_user.id, "ID Топика успешно изменён")
        except Exception as e: 
            bot.send_message(message.from_user.id, f"Произошла ошибка {e}")
        finally:
            db.close()
   