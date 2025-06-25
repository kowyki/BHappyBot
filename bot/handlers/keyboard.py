import sqlite3
from telebot import TeleBot, util
from telebot.types import Message

from ..classes import *
from ..keyboards.reply import no_kb, users_actions_markup, timer_actions_markup, chat_actions_markup
from ..data.main_data import timer_data
from ..methods.misc import modify_chats_markup
from ..methods.google import add_google_bot, table_sync
from ..methods.timer import start_timer
from ..methods.user import add_user, remove_user

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

            # bot.register_next_step_handler(message, chat_actions, bot, chat_id)

        case "Таймер":
            if timer_data:
                msg = f'Время создания таймера: {timer_data[chat_id.string][1]} \nВремя активации: {timer_data[chat_id.string][2]} \nВремя до активации: {timer_data[chat_id.string][3]}'
            else: msg = 'Таймер не активен'

            bot.send_message(message.from_user.id, msg, reply_markup=timer_actions_markup)
            bot.register_next_step_handler(message, timer_actions, bot, chat_id)

            # bot.register_next_step_handler(message, chat_actions, bot, chat_id)

        case "Добавить таблицы":
            bot.send_message(message.from_user.id, 'Отправьте файл с данными Google-бота', reply_markup=no_kb)
            bot.register_next_step_handler(message, add_google_bot, bot, chat_id)

            # bot.register_next_step_handler(message, chat_actions, bot, chat_id)

        case "Синхронизация с таблицами":
            bot.send_message(message.from_user.id, 'Введите название листа с пользователями', reply_markup=no_kb)
            bot.register_next_step_handler(message, table_sync, bot, chat_id)

            # bot.register_next_step_handler(message, chat_actions, bot, chat_id)

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

            # bot.register_next_step_handler(message, timer_actions, bot, chat_id)

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
            bot.send_message(message.from_user.id, 'Введите тег пользователя, имя и дату его рождения в формате: tag name d.m', reply_markup=no_kb)
            print(0)
            bot.register_next_step_handler(message, add_user, bot, chat_id)
            print(1)
            bot.register_next_step_handler(message, users_actions, bot, chat_id)
            print(2)

        case "Удалить":
            bot.send_message(message.from_user.id, 'Введите тег пользователя, которого необходимо удалить', reply_markup=no_kb)
            bot.register_next_step_handler(message, remove_user, bot, chat_id)

            # bot.register_next_step_handler(message, users_actions, bot, chat_id)

        case "Очистить":
            db = sqlite3.connect('bot/data/data.db')
            cursor = db.cursor()
            cursor.execute(f'DELETE FROM users_data_{chat_id.string}')
            db.commit()
            db.close()
            bot.send_message(message.from_user.id, 'Пользователи очищены')

            # bot.register_next_step_handler(message, users_actions, bot, chat_id)

        case "Назад":
            bot.send_message(message.from_user.id, f'Настройка чата', reply_markup=chat_actions_markup)

            bot.register_next_step_handler(message, chat_actions, bot, chat_id)
