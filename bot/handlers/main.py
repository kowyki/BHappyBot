import os
import datetime as dt
from dotenv import load_dotenv
from telebot import TeleBot, util
from telebot.types import Message

from ..data.user_data import *
from ..methods.misc import * 
from ..methods.sender import * 

if 'admins_id' not in globals():
    load_dotenv()
    admins_id = [os.getenv('ADMIN_ID_1'), os.getenv('ADMIN_ID_2')]

# Обработчик комманд
def commands_handler(message: Message, bot: TeleBot) -> None:
    # Проверка на админа
    if str(message.from_user.id) not in admins_id: return
    match message.text:
        case '/start':
            bot.send_message(message.from_user.id, 'Список комманд:\n/start - вывести список комманд \n/list - посмотреть список всех людей \n/add - добавить человека \n/remove - удалить человека \n/remove_all - удалить все данные \n/table_init - занести в список людей из таблицы \n/start_timer - запустить ежедневную проверку \n/id - вывести id чата и топика\n/upload_table - отправить таблицу')

        case '/list':
            global user_data
            ans = ''
            if user_data == {}: 
                bot.send_message(message.from_user.id, 'Пользователей нет')
            else: 
                for user_tag, bdate in user_data.items():
                    ans += f'@{user_tag} {bdate[0]}.{bdate[1]}\n'
                splitted_message = util.smart_split(ans, chars_per_string=3700)
                bot.send_message(message.from_user.id, splitted_message)

        case '/add':
            bot.send_message(message.from_user.id, 'Введите тег пользователя и дату его рождения в формате: tag d.m')
            bot.register_next_step_handler(message, add_user, bot)

        case '/remove':
            bot.send_message(message.from_user.id, 'Введите id пользователя, которого необходимо удалить')
            bot.register_next_step_handler(message, remove_user, bot)

        case '/remove_all':
            user_data = {}
            bot.send_message(message.from_user.id, 'Пользователи очищены')

        case '/table_init':
            bot.send_message(message.from_user.id, f'Введите название листа с пользователями')
            bot.register_next_step_handler(message, table_init, bot)

        case '/start_timer':
            try: 
                start_timer(bot)
                bot.send_message(message.from_user.id, f'Таймер запущен')
            except Exception as e:
                bot.send_message(message.from_user.id, f'Произошла ошибка {e}')

        case '/id':
            try: 
                print_id(message, bot)
            except Exception as e:
                bot.send_message(message.from_user.id, f'Произошла ошибка {e}')

        case '/upload_table':
            bot.send_message(message.from_user.id, 'Отправьте файл таблицы')
            bot.register_next_step_handler(message, upload_table, bot)

# Добавить пользователя
def add_user(message: Message, bot: TeleBot) -> None:
    try: 
        user_tag, user_bday = message.text.split()
        user_bday_day, user_bday_month = map(int, user_bday.split('.'))
        user_data[user_tag] = (user_bday_day, user_bday_month)

        bot.send_message(message.from_user.id, f'Пользователь @{user_tag} успешно добавлен')

    except:
        bot.send_message(message.from_user.id, f'Вы ввели данные в неверном формате')

# Удалить пользователя
def remove_user(message: Message, bot: TeleBot) -> None:
    user_tag = message.text
    try: del user_data[user_tag]
    except KeyError:
        bot.send_message(message.from_user.id, 'Пользователя с таким id не существует')

# Парсинг данных из таблицы
def table_init(message: Message, bot: TeleBot) -> None:
    sheet_name = message.text
    try: 
        bday_data = parse_from_table(sheet_name)
        add_users_from_table(bday_data)
        bot.send_message(message.from_user.id, 'Пользователи добавлены')
    except Exception as e:
        bot.send_message(message.from_user.id, f'Произошла ошибка {e}')

# Узнать ID чата и топика
def print_id(message: Message, bot: TeleBot) -> None:
    chat_id = message.chat.id
    try: msg_thread_id = message.reply_to_message.message_thread_id
    except AttributeError: msg_thread_id = "General"
    bot.send_message(message.from_user.id, f"Chat ID этого чата: {chat_id}\nИ message_thread_id: {msg_thread_id}")
    # print(f"Chat ID этого чата: {chat_id}\nИ message_thread_id: {msg_thread_id}")

# Загрузка таблицы
def upload_table(message: Message, bot: TeleBot) -> None:
    try:
        file_info = bot.get_file(message.document.file_id)
        d_file = bot.download_file(file_info.file_path)
        with open('files/table.xlsx', 'wb') as new_file:
            new_file.write(d_file)
            new_file.close()
        bot.send_message(message.from_user.id, f'Таблица успешно сохранена')

    except Exception as e:
        bot.send_message(message.from_user.id, f'Произошла ошибка {e}')
