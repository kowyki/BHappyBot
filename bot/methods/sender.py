import os, threading
import datetime as dt
from urllib.request import urlopen
from telebot import TeleBot
from dotenv import load_dotenv

from ..data.users_data import *

if 'CHAT_ID' not in globals():
    load_dotenv()
    CHAT_ID = int(os.getenv('CHAT_ID'))
    THREAD_ID = int(os.getenv('THREAD_ID'))

if 'timer_data' not in globals():
    timer_data = {}

# Получить дату и время
def get_today() -> dt.datetime:
    date = urlopen('http://just-the-time.appspot.com/').read().strip().decode('utf-8')
    now_gmt = dt.datetime.strptime(date, '%Y-%m-%d %X')
    now_mos = now_gmt.replace(hour=now_gmt.hour+3)
    return now_mos

# Запуск таймера
def start_timer(bot: TeleBot, seconds=None) -> None:
    now = get_today()
    time_send = now.replace(hour=9, minute=0, second=10, microsecond=0)

    delta = time_send - now
    if now.hour >= 9: delta += dt.timedelta(days=1)

    seconds = seconds or delta.total_seconds()

    timer_data['main'] = (threading.Timer(seconds, check_date, [bot]), f'{int(seconds//3600)}ч {int((seconds - (seconds//3600)*3600)//60)}м {int(seconds%60)}с', now.strftime('%d.%m %X'))
    timer_data['main'][0].start()


# Проверка даты
def check_date(bot: TeleBot) -> None:
    today = get_today()
    db = sqlite3.connect('bot/data/data.db')
    cursor = db.cursor()

    # Проверка на новый месяц 
    if today.day == 1:
        msg = []
        cursor.execute(f'SELECT * FROM users_data WHERE CAST(substr(dates, 4, 2) AS INTEGER) = {today.month}')
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

        bot.send_message(CHAT_ID, to_send, message_thread_id=THREAD_ID)
    
    # Проверка людей, у которых сегодня день рождения
    msg = []
    cursor.execute(f'SELECT * FROM users_data WHERE CAST(substr(dates, 4, 2) AS INTEGER) = {today.month} AND CAST(substr(dates, 1, 2) AS INTEGER) = {today.day}')
    users_data = cursor.fetchall()
    for user in users_data:
        msg.append(f'{user[2]} @{user[0]}, ')

    if len(msg) == 1:
        congrats_msg = f'Сегодня празднует свой день рождения {msg[0][:-2]}! 🥳'
        bot.send_message(CHAT_ID, congrats_msg, message_thread_id=THREAD_ID)

    elif len(msg) > 1:
        congrats_msg = f'Сегодня празднуют свой день рождения {"".join(msg[:-1])}'
        congrats_msg = f'{congrats_msg[:-2]} и {msg[-1][:-2]}! 🥳'
        bot.send_message(CHAT_ID, congrats_msg, message_thread_id=THREAD_ID)

    db.close()

    # Запуск таймера на 1 день
    start_timer(bot, dt.timedelta(days=1).total_seconds())
