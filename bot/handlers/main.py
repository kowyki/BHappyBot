import sqlite3, pygsheets
from telebot import TeleBot, util
from telebot.types import Message
from datetime import datetime as dt

from ..methods.timer import start_timer
from ..classes import *
from ..methods.misc import print_id, modify_chats_markup
from ..data.main_data import timer_data
from ..keyboards.reply import no_kb, users_actions_markup, timer_actions_markup, chat_actions_markup


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


def keyboard_handler(message: Message, bot: TeleBot) -> None:
    match message.text:
        case "Добавить чат":
            bot.send_message(message.from_user.id, f'Добавьте бота в нужный чат, после чего отправьте команду /id в топик, в который хотите чтобы бот присылал поздравления')

        case _:
            db = sqlite3.connect('bot/data/data.db')
            cursor = db.cursor()
            cursor.execute('SELECT chat_id, chat_title FROM admins WHERE admin_id = ?', [message.from_user.id])
            chats_data = cursor.fetchall()

            for data in chats_data:
                if message.text[:22] == data[1][:22]:
                    bot.send_message(message.from_user.id, f'Настройка чата', reply_markup=chat_actions_markup)
                    chat_id = Chat_ID(data[0])
                    bot.register_next_step_handler(message, chat_actions, bot, chat_id)
                    break
            

def chat_actions(message: Message, bot: TeleBot, chat_id: Chat_ID) -> None:
    match message.text:
        case "Пользователи":
            bot.send_message(message.from_user.id, f'Управление пользователями', reply_markup=users_actions_markup)
            bot.register_next_step_handler(message, users_actions, bot, chat_id)

        case "Таймер":
            if timer_data:
                msg = f'Время создания таймера: {timer_data[chat_id.string][1]} \nВремя активации: {timer_data[chat_id.string][2]} \nВремя до активации: {timer_data[chat_id.string][3]}'
            else: msg = 'Таймер не активен'

            bot.send_message(message.from_user.id, msg, reply_markup=timer_actions_markup)
            bot.register_next_step_handler(message, timer_actions, bot, chat_id)

        case "Добавить таблицы":
            bot.send_message(message.from_user.id, 'Отправьте файл с данными Google-бота', reply_markup=no_kb)
            bot.register_next_step_handler(message, add_google_bot, bot, chat_id)

        case "Синхронизация с таблицами":
            bot.send_message(message.from_user.id, 'Введите название листа с пользователями', reply_markup=no_kb)
            bot.register_next_step_handler(message, table_sync, bot, chat_id)

        case "Назад":
            chats_markup = modify_chats_markup(message.from_user.id)
            bot.send_message(message.from_user.id, f'Выбор чата', reply_markup=chats_markup)
            bot.register_next_step_handler(message, keyboard_handler, bot)


def timer_actions(message: Message, bot: TeleBot, chat_id: Chat_ID) -> None:
    match message.text:
        case 'Запуск':
            start_timer(bot, chat_id, seconds=None)
            bot.send_message(message.from_user.id, f'Время создания таймера: {timer_data[chat_id.string][1]} \nВремя активации: {timer_data[chat_id.string][2]} \nВремя до активации: {timer_data[chat_id.string][3]}')

            bot.register_next_step_handler(message, timer_actions, bot, chat_id)

        case 'Удалить':
            if chat_id.string in timer_data:
                del timer_data[chat_id.string]
                bot.send_message(message.from_user.id, f'Таймер удалён')

                bot.register_next_step_handler(message, timer_actions, bot, chat_id)

            else:
                bot.send_message(message.from_user.id, f'Таймер не создан')

                bot.register_next_step_handler(message, timer_actions, bot, chat_id)

        case 'Изменить время':
            bot.send_message(message.from_user.id, f'Напишите время по МСК, в которое хотите, чтобы бот присылал поздравления в формате ЧЧ:ММ:СС:МС', reply_markup=no_kb)
            bot.register_next_step_handler(message, change_send_time, bot, chat_id)

        case 'Назад':
            bot.send_message(message.from_user.id, f'Настройка чата', reply_markup=chat_actions_markup)
            bot.register_next_step_handler(message, chat_actions, bot, chat_id)


def change_send_time(message: Message, bot: TeleBot, chat_id: Chat_ID) -> None:
    try: 
        user_time = tuple(map(int, message.text.split(':')))
        start_timer(bot, chat_id, None, user_time)
        bot.send_message(message.from_user.id, f'Таймер успешно изменён \nВремя создания таймера: {timer_data[chat_id.string][1]} \nВремя активации: {timer_data[chat_id.string][2]} \nВремя до активации: {timer_data[chat_id.string][3]}', reply_markup=timer_actions_markup)

    except Exception as e:
        bot.send_message(message.from_user.id, f'Возникла ошибка {e}', reply_markup=timer_actions_markup)

    finally:
        bot.register_next_step_handler(message, timer_actions, bot, chat_id)


def users_actions(message: Message, bot: TeleBot, chat_id: Chat_ID) -> None:
    match message.text:
        case "Список":
            db = sqlite3.connect('bot/data/data.db')
            cursor = db.cursor()
            cursor.execute(f'SELECT * FROM users_data_{chat_id.string}')
            users_data = cursor.fetchall()
            db.close()

            if users_data == []: 
                bot.send_message(message.from_user.id, 'Пользователей нет')
            else: 
                ans = ''
                for item in users_data:
                    ans += f'{item[2]} {item[0]} {item[1]}\n'
                splitted_message = util.smart_split(ans, chars_per_string=3700)
                bot.send_message(message.from_user.id, splitted_message)

            bot.register_next_step_handler(message, users_actions, bot, chat_id)

        case "Добавить":
            bot.send_message(message.from_user.id, 'Введите тег пользователя, имя и дату его рождения в формате: @tag name d.m', reply_markup=no_kb)
            bot.register_next_step_handler(message, add_user, bot, chat_id)
            
        case "Удалить":
            bot.send_message(message.from_user.id, 'Введите тег пользователя, которого необходимо удалить', reply_markup=no_kb)
            bot.register_next_step_handler(message, remove_user, bot, chat_id)

        case "Очистить":
            db = sqlite3.connect('bot/data/data.db')
            cursor = db.cursor()
            cursor.execute(f'DELETE FROM users_data_{chat_id.string}')
            db.commit()
            db.close()
            bot.send_message(message.from_user.id, 'Пользователи очищены')
            bot.register_next_step_handler(message, users_actions, bot, chat_id)

        case "Назад":
            bot.send_message(message.from_user.id, f'Настройка чата', reply_markup=chat_actions_markup)
            bot.register_next_step_handler(message, chat_actions, bot, chat_id)


def add_user(message: Message, bot: TeleBot, chat_id: Chat_ID) -> None:
    try: 
        user_tag, user_name, user_bday = message.text.split()
        user_bday = dt.strptime(user_bday, "%d.%m")
        user_bday = user_bday.strftime("%d.%m")

        db = sqlite3.connect('bot/data/data.db')
        cursor = db.cursor()

        cursor.execute(f'INSERT INTO users_data_{chat_id.string} VALUES (?, ?, ?)', [user_tag, user_bday, user_name])
        db.commit()
        db.close()

        bot.send_message(message.from_user.id, f'Пользователь {user_tag} успешно добавлен', reply_markup=users_actions_markup)

    except Exception as e:
        bot.send_message(message.from_user.id, f'Вы ввели данные в неверном формате, {e}', reply_markup=users_actions_markup)

    finally:
        bot.register_next_step_handler(message, users_actions, bot, chat_id)


def remove_user(message: Message, bot: TeleBot, chat_id: Chat_ID) -> None:
    user_tag = message.text
    try: 
        db = sqlite3.connect('bot/data/data.db')
        cursor = db.cursor()

        cursor.execute(f'DELETE FROM users_data_{chat_id.string} WHERE user_tag = ?', [user_tag])
        db.commit()
        db.close()
        bot.send_message(message.from_user.id, f'Пользователь {user_tag} успешно удалён', reply_markup=users_actions_markup)

    except:
        bot.send_message(message.from_user.id, 'Пользователя с таким тегом не существует', reply_markup=users_actions_markup)

    finally:
        bot.register_next_step_handler(message, users_actions, bot, chat_id)


def parse_from_table(chat_id: Chat_ID, sheet="Днюшки") -> None:
    client = pygsheets.authorize(service_account_file=f"bot/data/{chat_id.string}.json")
    db = sqlite3.connect('bot/data/data.db')
    cursor = db.cursor()

    cursor.execute(f'SELECT google_sheets_link FROM admins WHERE chat_id = {chat_id.integer}')
    url = cursor.fetchall()[0][0]
    spreadsht = client.open_by_url(url)
    worksht = spreadsht.worksheet_by_title(sheet)

    data = list(zip(
        worksht.get_col(1), # Имя в формате всёчтоугодно ИМЯ
        worksht.get_col(2), # Дата рождения
        worksht.get_col(3) # Телеграм-тег
    ))

    data = [tup for tup in data[1:] if all(item != '' for item in tup)]
    filtered_data = [(tup[2], tup[1][:-5], (tup[0].split()[-1])) for tup in data]

    cursor.executemany(f'INSERT INTO users_data_{chat_id.string} VALUES (?, ?, ?)', filtered_data)
    db.commit()
    db.close()


def add_google_bot(message: Message, bot: TeleBot, chat_id: Chat_ID) -> None:
    file_info = bot.get_file(message.document.file_id)
    custom_path = 'bot/data/'
    file_path = custom_path + message.document.file_name
    downloaded_file = bot.download_file(file_info.file_path)

    with open(f'{custom_path}{chat_id.string}.json', 'wb') as f:
        f.write(downloaded_file)
    bot.send_message(message.from_user.id, 'Данные бота добавлены', reply_markup=no_kb)
    bot.send_message(message.from_user.id, 'Отправьте ссылку на Google таблицу с данными пользователей')

    bot.register_next_step_handler(message, add_google_sheets, bot, chat_id)


def add_google_sheets(message: Message, bot: TeleBot, chat_id: Chat_ID) -> None:
    link = message.text
    try:
        db = sqlite3.connect('bot/data/data.db')
        cursor = db.cursor()
        cursor.execute(f'UPDATE admins SET google_sheets_link = ? WHERE chat_id = ?', [link, chat_id.integer])
        db.commit()
        db.close()
        bot.send_message(message.from_user.id, 'Ссылка успешно добавлена', reply_markup=chat_actions_markup)

    except Exception as e: 
        bot.send_message(message.from_user.id, f'Произошла ошибка: {e}', reply_markup=chat_actions_markup)

    finally:
        bot.register_next_step_handler(message, chat_actions, bot, chat_id)


def table_sync(message: Message, bot: TeleBot, chat_id: Chat_ID):
    try:
        parse_from_table(chat_id, message.text)
        bot.send_message(message.from_user.id, 'Пользователи синхронизированы с данными в Google Sheets', reply_markup=chat_actions_markup)
    except Exception as e: 
        bot.send_message(message.from_user.id, f'Произошла ошибка {e}', reply_markup=chat_actions_markup)
    finally:
        bot.register_next_step_handler(message, chat_actions, bot, chat_id)
    