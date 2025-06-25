import sqlite3
from telebot import TeleBot
from telebot.types import Message
from datetime import datetime as dt

from ..classes import *
from ..keyboards.reply import users_actions_markup

def add_user(message: Message, bot: TeleBot, chat_id: Chat_ID) -> None:
    print(10)
    try: 
        user_tag, user_name, user_bday = message.text.split()
        user_bday = dt.strptime(user_bday, "%d.%m")
        user_bday = user_bday.strftime("%d.%m")

        db = sqlite3.connect('bot/data/data.db')
        cursor = db.cursor()

        cursor.execute(f'INSERT INTO users_data_{chat_id.string} VALUES (?, ?, ?)', [user_tag, user_bday, user_name])
        db.commit()
        db.close()

        bot.send_message(message.from_user.id, f'Пользователь @{user_tag} успешно добавлен', reply_markup=users_actions_markup)

    except Exception as e:
        bot.send_message(message.from_user.id, f'Вы ввели данные в неверном формате, {e}', reply_markup=users_actions_markup)

    finally: print(20)


def remove_user(message: Message, bot: TeleBot, chat_id: Chat_ID) -> None:
    user_tag = message.text
    try: 
        db = sqlite3.connect('bot/data/data.db')
        cursor = db.cursor()

        cursor.execute(f'DELETE FROM users_data_{chat_id.string} WHERE user_tag = ?', [user_tag])
        db.commit()
        db.close()
        bot.send_message(message.from_user.id, f'Пользователь @{user_tag} успешно удалён', reply_markup=users_actions_markup)

    except:
        bot.send_message(message.from_user.id, 'Пользователя с таким тегом не существует', reply_markup=users_actions_markup)

