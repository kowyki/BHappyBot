import sqlite3

def create_db():
    db = sqlite3.connect('bot/data/data.db')
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE users_data (
        user_tag TEXT,
        user_bday DATE,
        user_name TEXT
        )
    """)
    cursor.execute("""CREATE TABLE vars (
        var_name TEXT,
        var_value TEXT
        )
    """)
    db.commit()
    db.close()
