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
            bot.send_message(message.from_user.id, 'Список комманд: \n/start — вывести список комманд \n/list — посмотреть список всех пользователей \n/add — добавить пользователя \n/remove — удалить пользователя \n/clear — очистить данные \n/timer — запустить ежедневную проверку \n/table_upload — загрузить таблицу \n/table_init —  занести в базу данных пользователей из таблицы \n/info —  вывести основную информацию \n/id — вывести id чата и топика (данную команду необходимо написать в нужном чате')

        case '/list':
            global users_data
            if users_data == {}: 
                bot.send_message(message.from_user.id, 'Пользователей нет')
            else: 
                ans = ''
                for user_tag, user_data in users_data.items():
                    ans += f'{user_data[1]} {user_tag} {user_data[0][0]}.{user_data[0][1]}\n'
                splitted_message = util.smart_split(ans, chars_per_string=3700)
                bot.send_message(message.from_user.id, splitted_message)

        case '/add':
            bot.send_message(message.from_user.id, 'Введите тег пользователя, имя и дату его рождения в формате: tag name d.m')
            bot.register_next_step_handler(message, add_user, bot)

        case '/remove':
            bot.send_message(message.from_user.id, 'Введите тег пользователя, которого необходимо удалить')
            bot.register_next_step_handler(message, remove_user, bot)

        case '/clear':
            users_data.clear()
            bot.send_message(message.from_user.id, 'Пользователи очищены')

        case '/timer':
            try: 
                start_timer(bot)
                bot.send_message(message.from_user.id, f'Таймер запущен')
            except Exception as e:
                bot.send_message(message.from_user.id, f'Произошла ошибка {e}')

        case '/table_upload':
            bot.send_message(message.from_user.id, 'Отправьте файл таблицы')
            bot.register_next_step_handler(message, table_upload, bot)

        case '/table_init':
            dir_path = os.path.dirname(os.path.realpath(__file__))
            dir_path = dir_path[:dir_path.index('bot')]
            if not os.path.exists(dir_path+'files'):
                bot.send_message(message.from_user.id, f'Вы не добавили таблицу')
                return

            bot.send_message(message.from_user.id, f'Введите название листа с пользователями')
            bot.register_next_step_handler(message, table_init, bot)

        case '/info':
            msg = []
            # Информация о таймере
            if 'main' in timer_data:
                msg.append(f'Время создания таймера: {timer_data["main"][2]}')
                msg.append(f'Время до активации: {timer_data["main"][1]}')
            else: msg.append('Таймер не активен')

            # Наличие пользователей
            if users_data != {}: msg.append('Пользователи есть')
            else: msg.append('Пользователей нет')

            # Наличие папки
            dir_path = os.path.dirname(os.path.realpath(__file__))
            dir_path = dir_path[:dir_path.index('bot')]
            if not os.path.exists(dir_path+'files'):
                msg.append('Папка "files" отсутствует')
            else: msg.append('Папка "files" создана')

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
        user_bday_day, user_bday_month = map(int, user_bday.split('.'))
        users_data[user_tag] = ((user_bday_day, user_bday_month), user_name)

        bot.send_message(message.from_user.id, f'Пользователь @{user_tag} успешно добавлен')

    except:
        bot.send_message(message.from_user.id, f'Вы ввели данные в неверном формате')

# Удалить пользователя
def remove_user(message: Message, bot: TeleBot) -> None:
    user_tag = message.text
    try: 
        del users_data[user_tag]
        bot.send_message(message.from_user.id, 'Пользователь успешно удалён')
    except KeyError:
        bot.send_message(message.from_user.id, 'Пользователя с таким тегом не существует')

# Загрузка таблицы
def table_upload(message: Message, bot: TeleBot) -> None:
    try:
        file_info = bot.get_file(message.document.file_id)
        d_file = bot.download_file(file_info.file_path)

        dir_path = os.path.dirname(os.path.realpath(__file__))
        dir_path = dir_path[:dir_path.index('bot')]
        if not os.path.exists(dir_path+'files'):
            os.mkdir(dir_path+'files')

        with open(f'{dir_path}files/table.xlsx', 'wb') as new_file:
            new_file.write(d_file)
            new_file.close()
        bot.send_message(message.from_user.id, f'Таблица успешно сохранена')

    except Exception as e:
        bot.send_message(message.from_user.id, f'Произошла ошибка {e}')

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
