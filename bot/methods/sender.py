import datetime as dt
import os, threading
from telebot import TeleBot
from dotenv import load_dotenv

from ..data.user_data import *

if 'CHAT_ID' not in globals():
    load_dotenv()
    CHAT_ID = int(os.getenv('CHAT_ID'))
    THREAD_ID = int(os.getenv('THREAD_ID'))

# Запуск таймера
def start_timer(bot: TeleBot, seconds=None) -> None: 
    now = dt.datetime.now()
    time_send = dt.datetime.strptime(f'{now.date()} 9:{now.minute}:{now.second}', '%Y-%m-%d %H:%M:%S')

    delta = time_send - now
    if now.hour >= 9: delta += dt.timedelta(days=1)

    seconds = seconds or delta.total_seconds()

    main_timer = threading.Timer(seconds, check_date, [bot])
    main_timer.start()

# Проверка даты
def check_date(bot: TeleBot) -> None:
    today = dt.date.now()
    # Проверка на новый месяц 
    if today.day == 1:
        msg = []
        for user_tag, bdate in user_data.items():
            if bdate[1] == today.month: msg.append((bdate.day, user_tag))

        if msg == []: start_timer(bot, dt.timedelta(days=1).total_seconds())

        msg.sort(key=lambda x: x[0])
        to_send = 'В этом месяце день рождения у: \n'
        for x in msg: to_send += f'{x[0]} @{x[1]}\n'

        bot.send_message(CHAT_ID, to_send, message_thread_id=THREAD_ID)
    
    # Проверка людей, у которых сегодня день рождения
    msg = ''
    for user_tag, bdate in user_data.items():
        if bdate[1] == today.day:
            msg += f'@{user_tag}, '

    if msg != '':
        msg = f'Сегодня день рождения у {msg[:-2]}! Поздравлям 🥳🎉'
        bot.send_message(CHAT_ID, msg, message_thread_id=THREAD_ID)

    # Запуск таймера на 1 день
    start_timer(bot, dt.timedelta(days=1).total_seconds())
