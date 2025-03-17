import aiosqlite


async def insert_data_to_db(data: list[tuple]) -> None:
    """Функция для асинхронной вставки данных в базу данных SQLite."""
    async with aiosqlite.connect('products.db') as conn:
        async with conn.cursor() as cursor:
            # Создание таблицы, если она не существует
            await cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                url TEXT,
                xpath TEXT,
                price REAL
            )
            ''')

            # Вставка данных
            await cursor.executemany('''
            INSERT INTO products (title, url, xpath, price)
            VALUES (?, ?, ?, ?)
            ''', data)

            await conn.commit()
