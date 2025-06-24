import pygsheets

from ..data.users_data import *

# Спарсить из таблицы данные о людях
def parse_from_table(sheet="Днюшки") -> None:
    client = pygsheets.authorize(service_account_file="c:\\Users\\kowyki\\Desktop\\bhappybot-04566439ff2d.json")
    spreadsht = client.open_by_url("https://docs.google.com/spreadsheets/d/1JFHMoLJEuOrE8m67uBcl9YuTtGwD6KJDHRb1G7wwNww/")
    worksht = spreadsht.worksheet_by_title(sheet)

    data = list(zip(
        worksht.get_col(2),
        worksht.get_col(3),
        worksht.get_col(5)
    ))

    data = [tup for tup in data[1:] if all(item != '' for item in tup)]
    filtered_data = [(tup[2], tup[1][:-5], (tup[0].split()[-1])) for tup in data]

    db = sqlite3.connect('bot/data/data.db')
    cursor = db.cursor()
    cursor.executemany(f'INSERT INTO users_data VALUES (?, ?, ?)', filtered_data)
    db.commit()
    db.close()

