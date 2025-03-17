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
                price REAL,
                batch_id INTEGER
            )
            ''')
            await cursor.execute("SELECT COALESCE(MAX(batch_id), 0) + 1 FROM products")
            new_batch_id = (await cursor.fetchone())[0]
            data_with_batch = [(title, url, xpath, price, new_batch_id) for title, url, xpath, price in data]
            await cursor.executemany('''
            INSERT INTO products (title, url, xpath, price, batch_id)
            VALUES (?, ?, ?, ?, ?)
            ''', data_with_batch)

            await conn.commit()


async def get_avg_price_from_last_file() -> float:
    """Функция для получения средней цены товаров из последней загрузки."""
    async with aiosqlite.connect('products.db') as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT MAX(batch_id) FROM products")
            last_batch = await cursor.fetchone()

        if not last_batch or last_batch[0] is None:
            return None

        async with conn.cursor() as cursor:
            await cursor.execute("SELECT AVG(price) FROM products WHERE batch_id = ?", (last_batch[0],))
            avg_price = await cursor.fetchone()

        return avg_price[0] if avg_price else None
