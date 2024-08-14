import json
import pandas as pd
import datetime as dt

def parse_from_table():
    excel = pd.read_excel("format/suirBDay.xlsx", sheet_name="BDay", usecols=[2,4], parse_dates=[0], date_format='%d-%m-%Y')

    data_list = excel.to_dict(orient='records')

    with open(f'format/out.json', 'w', encoding='utf-8') as f:
        json.dump(data_list, f, indent=4, ensure_ascii=False)

    bday_data = {}
    for user in data_list: 
        try:
            tg = user['Телега']
            user_tag = tg[tg.index('@')+1:].strip()

            bdate = user['Дата рождения (дд.гг)']
            bday = bdate[bdate.index('-')+1:bdate.index(' ')]
            bday = bday.split('-')[::-1]

            bday_data[user_tag] = bday

        except: ...

    return bday_data







