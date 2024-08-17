import os, json
import pandas as pd

from ..data.users_data import *

# Добавить в базу людей из таблицы
def add_users_from_table(table:dict) -> None:
    for user_tag, user_data in table.items():
        users_data[user_tag] = user_data

# Спарсить из таблицы данные о людях
def parse_from_table() -> dict:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = dir_path[:dir_path.index('bot')]

    excel = pd.read_excel(f'{dir_path}files/table.xlsx', sheet_name=sheet, usecols=[1,2,4], parse_dates=[1], date_format='%d-%m-%Y')

    data_list = excel.to_dict(orient='records')

    bday_data = {}
    for user in data_list: 
        try:
            uname = user['ФИ']
            user_name = uname.split()[-1]

            tg = user['Телега']
            user_tag = tg[tg.index('@')+1:].strip()

            bdate = user['Дата рождения (дд.гг)']
            bday = bdate[bdate.index('-')+1:bdate.index(' ')]
            bday = tuple(map(int, bday.split('-')[::-1]))

            bday_data[user_tag] = (bday, user_name)

        except Exception as e: ... # print(e)

    return bday_data
