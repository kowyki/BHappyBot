import sqlite3

def create_db():
    db = sqlite3.connect('bot/data/data.db')
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE admins (
        admin_id INTEGER,
        chat_id INTEGER,
        thread_id INTGER,
        chat_title TEXT,
        google_sheets_link TEXT
        )
    """)

    db.commit()
    db.close()


if 'timer_data' not in globals():
    global timer_data
    timer_data = {}
