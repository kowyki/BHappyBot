import pygsheets

from ..data.users_data import *

# Спарсить из таблицы данные о людях
def parse_from_table(sheet="Днюшки") -> None:
    client = pygsheets.authorize(service_account_file="client.json")
    db = sqlite3.connect('bot/data/data.db')
    cursor = db.cursor()
    cursor.execute('SELECT var_value FROM vars WHERE var_name = "google_sheets_link"')
    url = cursor.fetchall()
    spreadsht = client.open_by_url(url)
    worksht = spreadsht.worksheet_by_title(sheet)

    data = list(zip(
        worksht.get_col(1),
        worksht.get_col(2),
        worksht.get_col(3)
    ))

    data = [tup for tup in data[1:] if all(item != '' for item in tup)]
    filtered_data = [(tup[2], tup[1][:-5], (tup[0].split()[-1])) for tup in data]

    cursor.executemany(f'INSERT INTO users_data VALUES (?, ?, ?)', filtered_data)
    db.commit()
    db.close()
