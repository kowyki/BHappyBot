import pygsheets, sqlite3
from telebot import TeleBot
from telebot.types import Message

from ..classes import *
from ..keyboards.reply import no_kb, chat_actions_markup

# Спарсить из таблицы данные о людях
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


def table_sync(message: Message, bot: TeleBot, chat_id: Chat_ID):
    try:
        parse_from_table(chat_id, message.text)
        bot.send_message(message.from_user.id, 'Пользователи синхронизированы с данными в Google Sheets', reply_markup=chat_actions_markup)
    except Exception as e: 
        bot.send_message(message.from_user.id, f'Произошла ошибка {e}', reply_markup=chat_actions_markup)
