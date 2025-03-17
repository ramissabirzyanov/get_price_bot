import sqlite3


def insert_data_to_db(data):
    """Функция для вставки данных в базу данных SQLite."""
    conn = sqlite3.connect('product_prices.db')
    cursor = conn.cursor()

    # Создание таблицы (если она не существует)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        url TEXT,
        xpath TEXT,
        price REAL
    )
    ''')

    cursor.executemany('''INSERT INTO products (title, url, xpath, price) VALUES (?, ?, ?, ?)''', data)
    conn.commit()
    conn.close()