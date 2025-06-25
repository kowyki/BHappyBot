import sqlite3
from telebot import TeleBot
from telebot.types import Message

from ..methods.timer import start_timer
from ..classes import *
from .keyboard import modify_chats_markup
from ..methods.misc import print_id


def commands_handler(message: Message, bot: TeleBot) -> None:
    match message.text:
        case '/start':
            chats_markup = modify_chats_markup(message.from_user.id)

            bot.send_message(message.from_user.id, 'Список комманд: \n/start — вывести список комманд \n/list — посмотреть список всех пользователей \n/add — добавить пользователя \n/remove — удалить пользователя \n/clear — очистить данные \n/timer — запустить ежедневную проверку \n/add_google_sheets — добавить ссылку на Google Таблицу с данными пользователей. В первом столбце ФИ, во втором дата рождения, в третьем телеграм-тег \n/table_sync — синхронизация данных о пользователях с облаком Google Таблиц \n/info — вывести основную информацию \n/id — вывести id чата и топика (данную команду необходимо написать в нужном чате', reply_markup=chats_markup)
                  
        case '/id':
            try: 
                print_id(message, bot)
            except Exception as e:
                bot.send_message(message.from_user.id, f'Произошла ошибка {e}')


def adding_to_chat_handler(message: Message, bot: TeleBot):
    for user in message.new_chat_members:
        if user.id == bot.get_me().id: break
    else: return

    chat_id = Chat_ID(message.chat.id)
    thread_id = "General"
    chat_title = message.chat.title

    db = sqlite3.connect('bot/data/data.db')
    cursor = db.cursor()
    cursor.execute(f'INSERT INTO admins VALUES (?, ?, ?, ?, ?)', [message.from_user.id, chat_id.integer, thread_id, chat_title, None])
    cursor.execute(f"""CREATE TABLE users_data_{chat_id.string} (
        user_tag TEXT,
        user_bday DATE,
        user_name TEXT
        )
    """)
    db.commit()
    db.close()

    start_timer(bot, chat_id)

    chats_markup = modify_chats_markup(message.from_user.id)
    bot.send_message(message.from_user.id, f'Чат {chat_title} успешно добавлен', reply_markup=chats_markup)


def removing_from_chat_handler(message: Message, bot: TeleBot):
    if message.left_chat_member.id != bot.get_me().id: return

    chat_id = Chat_ID(message.chat.id)
    chat_title = message.chat.title

    db = sqlite3.connect('bot/data/data.db')
    cursor = db.cursor()

    cursor.execute(f'DROP TABLE IF EXISTS users_data_{chat_id.string}')
    cursor.execute(f'DELETE FROM admins WHERE chat_id = ?', [chat_id.integer])
    db.commit()
    db.close()

    chats_markup = modify_chats_markup(message.from_user.id)
    bot.send_message(message.from_user.id, f'Чат {chat_title} удалён', reply_markup=chats_markup)
