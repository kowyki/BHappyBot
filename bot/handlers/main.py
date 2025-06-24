import os
from dotenv import load_dotenv
from telebot import TeleBot, util
from telebot.types import Message

from ..data.users_data import *
from ..methods.misc import * 
from ..methods.sender import * 

if 'admins_id' not in globals():
    load_dotenv()
    admin_ids = list(map(int, os.getenv('ADMIN_IDS').split()))

# Обработчик комманд
def commands_handler(message: Message, bot: TeleBot) -> None:
    # Проверка на админа
    if message.from_user.id not in admin_ids: return
    match message.text:
        case '/start':
            bot.send_message(message.from_user.id, 'Список комманд: \n/start — вывести список комманд \n/list — посмотреть список всех пользователей \n/add — добавить пользователя \n/remove — удалить пользователя \n/clear — очистить данные \n/timer — запустить ежедневную проверку \n/table_sync — синхронизация данных о пользователях с облаком Google Sheets \n/info — вывести основную информацию \n/id — вывести id чата и топика (данную команду необходимо написать в нужном чате')

        case '/list':
            db = sqlite3.connect('bot/data/data.db')
            cursor = db.cursor()
            cursor.execute(f'SELECT * FROM users_data')
            users_data = cursor.fetchall()
            db.close()

            if users_data == []: 
                bot.send_message(message.from_user.id, 'Пользователей нет')
            else: 
                ans = ''
                for item in users_data:  
                    ans += f'{item[2]} @{item[0]} {item[1]}\n'
                splitted_message = util.smart_split(ans, chars_per_string=3700)
                bot.send_message(message.from_user.id, splitted_message)

        case '/add':
            bot.send_message(message.from_user.id, 'Введите тег пользователя, имя и дату его рождения в формате: tag name d.m')
            bot.register_next_step_handler(message, add_user, bot)

        case '/remove':
            bot.send_message(message.from_user.id, 'Введите тег пользователя, которого необходимо удалить')
            bot.register_next_step_handler(message, remove_user, bot)

        case '/clear':
            db = sqlite3.connect('bot/data/data.db')
            cursor = db.cursor()
            cursor.execute('DELETE FROM users_data')
            db.commit()
            db.close()
            bot.send_message(message.from_user.id, 'Пользователи очищены')

        case '/timer':
            try: 
                start_timer(bot)
                bot.send_message(message.from_user.id, f'Таймер запущен')
            except Exception as e:
                bot.send_message(message.from_user.id, f'Произошла ошибка {e}')

        case '/table_sync':
            try:
                parse_from_table()
                bot.send_message(message.from_user.id, 'Пользователи синхронизированы с данными в Google Sheets')
            except: 
                bot.send_message(message.from_user.id, 'Произошла ошибка')

        case '/info':
            msg = []
            # Информация о таймере
            if timer_data:
                msg.append(f'Время создания таймера: {timer_data[2]}')
                msg.append(f'Время до активации: {timer_data[1]}')
            else: msg.append('Таймер не активен')

            # Наличие пользователей
            db = sqlite3.connect('bot/data/data.db')
            cursor = db.cursor()
            cursor.execute(f'SELECT * FROM users_data')
            users_data = cursor.fetchall()
            db.close()

            if users_data != []: msg.append('Пользователи есть')
            else: msg.append('Пользователей нет')

            bot.send_message(message.from_user.id, '\n'.join(msg))

        case '/id':
            try: 
                print_id(message, bot)
            except Exception as e:
                bot.send_message(message.from_user.id, f'Произошла ошибка {e}')


# Добавить пользователя
def add_user(message: Message, bot: TeleBot) -> None:
    try: 
        user_tag, user_name, user_bday = message.text.split()
        user_bday = dt.datetime.strptime(user_bday, "%d.%m")
        user_bday = user_bday.strftime("%d.%m")

        db = sqlite3.connect('bot/data/data.db')
        cursor = db.cursor()
        cursor.execute(f'INSERT INTO users_data VALUES (?, ?, ?)', [user_tag, user_bday, user_name])
        db.commit()
        db.close()

        bot.send_message(message.from_user.id, f'Пользователь @{user_tag} успешно добавлен')

    except:
        bot.send_message(message.from_user.id, 'Вы ввели данные в неверном формате')


# Удалить пользователя
def remove_user(message: Message, bot: TeleBot) -> None:
    user_tag = message.text
    try: 
        db = sqlite3.connect('bot/data/data.db')
        cursor = db.cursor()
        cursor.execute(f'DELETE FROM users_data WHERE user_tag = ?', [user_tag])
        db.commit()
        db.close()
        bot.send_message(message.from_user.id, f'Пользователь @{user_tag} успешно удалён')
    except:
        bot.send_message(message.from_user.id, 'Пользователя с таким тегом не существует')


# Узнать ID чата и топика
def print_id(message: Message, bot: TeleBot) -> None:
    chat_id = message.chat.id
    try: msg_thread_id = message.reply_to_message.message_thread_id
    except AttributeError: msg_thread_id = "General"
    bot.send_message(message.from_user.id, f"Chat ID этого чата: {chat_id}\nИ message_thread_id: {msg_thread_id}")
