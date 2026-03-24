import sqlite3


def create_db():
    # Connect to (or create) the database file
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # FIX: It must be "IF NOT EXISTS" (plural)
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT NOT NULL,
                     email TEXT UNIQUE,
                     password TEXT NOT NULL
                 )''')

    conn.commit()
    conn.close()
    print('Database and table created successfully!')


if __name__ == '__main__':
    create_db()