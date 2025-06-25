import threading, sqlite3
import datetime as dt
from urllib.request import urlopen
from telebot import TeleBot

from ..classes import *
from ..data.main_data import timer_data

# Получить дату и время
def get_today() -> dt.datetime:
    date = urlopen('http://just-the-time.appspot.com/').read().strip().decode('utf-8')
    now_gmt = dt.datetime.strptime(date, '%Y-%m-%d %X')
    now_mos = now_gmt + dt.timedelta(hours=3)
    return now_mos


# Запуск таймера
def start_timer(bot: TeleBot, chat_id: Chat_ID, seconds=None, send_time=(9, 0, 10, 0)) -> None:
    now = get_today()
    time_send = now.replace(hour=send_time[0], minute=send_time[1], second=send_time[2], microsecond=send_time[3])

    delta = time_send - now
    
    if time_send <= now: 
        delta += dt.timedelta(days=1)
        time_send += dt.timedelta(days=1)

    seconds = seconds or delta.total_seconds()

    timer = threading.Timer(seconds, check_date, [bot, chat_id])
    creation_time = now.strftime('%d.%m %X')
    activation_time = time_send.strftime('%d.%m %X')
    remaining_time = f'{int(seconds//3600)}ч {int((seconds - (seconds//3600)*3600)//60)}м {int(seconds%60)}с'
    
    timer_data[chat_id.string] = [timer, creation_time, activation_time, remaining_time]
    timer_data[chat_id.string][0].start()


# Проверка даты
def check_date(bot: TeleBot, chat_id: Chat_ID) -> None:
    today = get_today()
    db = sqlite3.connect('bot/data/data.db')
    cursor = db.cursor()

    cursor.execute('SELECT thread_id FROM admins WHERE chat_id = ?', [chat_id.integer])
    thread_id = str(cursor.fetchall()[0][0])

    # Проверка на новый месяц 
    if today.day == 1:
        msg = []
        cursor.execute(f'SELECT * FROM users_data_{chat_id.string} WHERE CAST(substr(user_bday, 4, 2) AS INTEGER) = {today.month}')
        users_data = cursor.fetchall()

        for user in users_data:
            user_bday = dt.datetime.strptime(user[1], '%d.%m')
            msg.append((user[2], user[0], user_bday.day))

        if msg == []: 
            to_send = 'В этом месяце ни у кого нет дней рождения :('
        else: 
            msg.sort(key=lambda x: x[2])
            to_send = 'Всем привет! В этом месяце родились: \n'
            for x in msg: to_send += f'- {x[0]} @{x[1]} {x[2]} числа\n'

        bot.send_message(chat_id.integer, to_send, message_thread_id=thread_id)
    
    # Проверка людей, у которых сегодня день рождения
    msg = []
    cursor.execute(f'SELECT * FROM users_data_{chat_id.string} WHERE CAST(substr(user_bday, 4, 2) AS INTEGER) = {today.month} AND CAST(substr(user_bday, 1, 2) AS INTEGER) = {today.day}')
    users_data = cursor.fetchall()
    for user in users_data:
        msg.append(f'{user[2]} @{user[0]}, ')

    if len(msg) == 1:
        congrats_msg = f'Сегодня празднует свой день рождения {msg[0][:-2]}! 🥳'
        bot.send_message(chat_id.integer, congrats_msg, message_thread_id=thread_id)

    elif len(msg) > 1:
        congrats_msg = f'Сегодня празднуют свой день рождения {"".join(msg[:-1])}'
        congrats_msg = f'{congrats_msg[:-2]} и {msg[-1][:-2]}! 🥳'
        bot.send_message(chat_id.integer, congrats_msg, message_thread_id=thread_id)

    db.close()

    # Запуск таймера на 1 день
    start_timer(bot, chat_id, dt.timedelta(days=1).total_seconds())
