import datetime as dt
import threading, os
from telebot import TeleBot
from dotenv import load_dotenv

load_dotenv()
CHAT_ID = int(os.getenv('CHAT_ID'))
THREAD_ID = int(os.getenv('THREAD_ID'))

if 'user_data' not in globals():
    user_data = {}
if 'timers' not in globals():
    timers = {}

def send_congrat(bot: TeleBot, user_tag):
    bot.send_message(CHAT_ID, f'Сегодня день рождения у @{user_tag}! Поздравлям 🥳🎉', message_thread_id=THREAD_ID)

    now_year = int(dt.datetime.today().year)
    user_bday = user_data[user_tag].strftime('%d.%m')
    user_bday_day, user_bday_month = map(int, user_bday.split('.'))

    user_data[user_tag] = dt.datetime.strptime(f'{user_bday_day}.{user_bday_month}.{now_year+1} 9', '%d.%m.%Y %H')
    delta = user_data[user_tag] - now

    start_timer(delta.total_seconds(), bot, user_tag)

def add_user(message, bot):
    try:
        # Преобразуем введенную дату в формат datetime
        user_tag, user_bday = message.text.split()
        user_bday_day, user_bday_month = map(int, user_bday.split('.'))
        now = dt.datetime.today()
        now_year = int(now.year)
        user_data[user_tag] = dt.datetime.strptime(f'{user_bday_day}.{user_bday_month}.{now_year} 9', '%d.%m.%Y %H')
        delta = user_data[user_tag] - now

        # Если введенная дата наступит в следующем году
        if delta.total_seconds() <= 0:
            user_data[user_tag] = dt.datetime.strptime(f'{user_bday_day}.{user_bday_month}.{now_year+1} 9', '%d.%m.%Y %H')
            delta = user_data[user_tag] - now

        start_timer(delta.total_seconds(), bot, user_tag)
        bot.send_message(message.from_user.id, f'До дня рождения данного пользователя осталось {delta}')
        # start_timer(5, bot, user_tag)

    # Если пользователь ввел некорректную дату и время, выводим сообщение об ошибке
    except ValueError:
        bot.send_message(message.from_user.id, 'Вы ввели неверный формат, попробуйте еще раз.')

def add_users_from_table(table, bot):
    for user_tag, user_bday in table.items():
        # Преобразуем введенную дату в формат datetime
        user_bday_day, user_bday_month = map(int, user_bday)
        now = dt.datetime.today()
        now_year = int(now.year)
        user_data[user_tag] = dt.datetime.strptime(f'{user_bday_day}.{user_bday_month}.{now_year} 9', '%d.%m.%Y %H')
        delta = user_data[user_tag] - now

        # Если введенная дата наступит в следующем году
        if delta.total_seconds() <= 0:
            user_data[user_tag] = dt.datetime.strptime(f'{user_bday_day}.{user_bday_month}.{now_year+1} 9', '%d.%m.%Y %H')
            delta = user_data[user_tag] - now

        start_timer(delta.total_seconds(), bot, user_tag)
        # start_timer(5, bot, user_tag)

def remove_user(message):
    user_tag = message.text
    timers[user_tag].cancel()
    del timers[user_tag]
    del user_data[user_tag]

def start_timer(timer, bot, user_tag):
    timers[user_tag] = threading.Timer(timer, send_congrat, [bot, user_tag])
    timers[user_tag].start()
