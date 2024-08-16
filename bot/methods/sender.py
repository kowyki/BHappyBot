import datetime as dt
import os, threading
from telebot import TeleBot
from dotenv import load_dotenv

from ..data.users_data import *

if 'CHAT_ID' not in globals():
    load_dotenv()
    CHAT_ID = int(os.getenv('CHAT_ID'))
    THREAD_ID = int(os.getenv('THREAD_ID'))

# Запуск таймера
def start_timer(bot: TeleBot, seconds=None) -> None: 
    now = dt.datetime.now()
    time_send = dt.datetime.strptime(f'{now.date()} 9:0:0', '%Y-%m-%d %X')

    delta = time_send - now
    if now.hour >= 9: delta += dt.timedelta(days=1)

    seconds = seconds or delta.total_seconds()

    main_timer = threading.Timer(seconds, check_date, [bot])
    main_timer.start()

# Проверка даты
def check_date(bot: TeleBot) -> None:
    today = dt.date.today()
    # Проверка на новый месяц 
    if today.day == 1:
        msg = []
        for user_tag, user_data in users_data.items():
            if user_data[0][1] == today.month: msg.append((user_data[0][0], user_tag, user_data[1]))

        if msg == []: 
            to_send = 'В этом месяце ни у кого нет дней рождения :('
        else: 
            msg.sort(key=lambda x: x[0])
            to_send = 'Всем привет! В этом месяце родились: \n'
            for x in msg: to_send += f'- {x[2]} @{x[1]} {x[0]} числа\n'

        bot.send_message(CHAT_ID, to_send, message_thread_id=THREAD_ID)
    
    # Проверка людей, у которых сегодня день рождения
    msg = []
    for user_tag, user_data in users_data.items():
        if user_data[0][0] == today.day and user_data[0][1] == today.month:
            msg.append(f'{user_data[1]} @{user_tag}, ')

    if len(msg) == 1:
        congrats_msg = f'Сегодня празднует свой день рождения {msg[0][:-2]}!🥳'
        bot.send_message(CHAT_ID, congrats_msg, message_thread_id=THREAD_ID)

    elif len(msg) > 1:
        congrats_msg = f'Сегодня празднуют свой день рождения {"".join(msg[:-1])}'
        congrats_msg = f'{congrats_msg[:-2]} и {msg[-1][:-2]}!🥳'
        bot.send_message(CHAT_ID, congrats_msg, message_thread_id=THREAD_ID)

    # Запуск таймера на 1 день
    start_timer(bot, dt.timedelta(days=1).total_seconds())
