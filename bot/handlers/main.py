import datetime as dt
from telebot import TeleBot, util
from telebot.types import Message

from ..methods.admin import * 
from format.table_format import *

if 'admins_id' not in globals():
    admins_id = [os.getenv('ADMIN_ID_1'), os.getenv('ADMIN_ID_2')]

def start_month_timer(bot):
    if dt.date.today().month == 12:
        next_month = dt.datetime.strptime(f'01.01.{dt.date.today().year+1} 9', '%d.%m.%Y %H')
    else:
        next_month = dt.datetime.strptime(f'01.{dt.date.today().month+1}.{dt.date.today().year} 9', '%d.%m.%Y %H')
    delta = next_month - dt.datetime.today()

    month_timer = threading.Timer(delta.total_seconds(), send_month_congrats, [bot])
    month_timer.start()

def send_month_congrats(bot):
    msg = []
    now_month = dt.date.today().month
    for user_tag, bdate in user_data.items():
        if bdate.month == now_month: msg.append((bdate.day, user_tag))

    msg.sort(key=lambda x: x[0])
    to_send = 'В этом месяце день рождения у: \n'
    for x in msg: to_send += f'{x[0]} @{x[1]}\n'

    bot.send_message(CHAT_ID, to_send, message_thread_id=THREAD_ID)
    start_month_timer(bot)

def commands_handler_admin(message: Message, bot: TeleBot):
    if str(message.from_user.id) not in admins_id: 
        # bot.send_message(message.from_user.id, 'Вы не являетесь администратором')
        return

    match message.text:
        case '/start':
            bot.send_message(message.from_user.id, 'Список комманд:\n/start - вывести список комманд \n/month_list - отправить сообщение об именинниках в этом месяце в чат \n/list - посмотреть список всех людей \n/add - добавить человека \n/remove - удалить человека \n/remove_all - удалить все данные \n/table_init - занести в список людей из таблицы')

        case '/month_list':
            send_month_congrats(bot)

        case '/list':
            ans = ''
            for user_tag, bdate in user_data.items():
                delta = bdate - dt.datetime.today()
                ans += f'@{user_tag} {bdate} {delta}\n'
            splitted_message = util.smart_split(ans, chars_per_string=3700)
            bot.send_message(message.from_user.id, splitted_message)

        case '/add':
            bot.send_message(message.from_user.id, 'Введите тег пользователя и дату его рождения в формате: tag d.m')
            bot.register_next_step_handler(message, add_user, bot)

        case '/remove':
            bot.send_message(message.from_user.id, 'Введите id пользователя, которого необходимо удалить')
            bot.register_next_step_handler(message, remove_user)

        case '/remove_all':
            remove_all()

        case '/table_init':
            bday_data = parse_from_table()
            add_users_from_table(bday_data, bot)
