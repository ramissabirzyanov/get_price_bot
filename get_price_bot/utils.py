import pandas
from get_price_bot.parser import get_price
from get_price_bot.db import insert_data_to_db, get_avg_price_from_last_file


def read_excel_file(file_path: str) -> pandas.DataFrame:
    df = pandas.read_excel(file_path, engine="openpyxl")

    required_columns = ['title', 'url', 'xpath']
    if not all(col in df.columns for col in required_columns):
        raise ValueError("Ошибка! Файл должен содержать колонки: title, url, xpath.")
    return df


async def get_data_and_insert_to_db(df: pandas.DataFrame) -> str:
    data_to_insert = []
    for row in df.itertuples(index=False):
        title = row.title
        url = row.url
        xpath = row.xpath
        price = get_price(url, xpath)
        data_to_insert.append((title, url, xpath, price))

    await insert_data_to_db(data_to_insert)
    return ("Файл успешно загружен и данные добавлены в базу данных.")


async def avg_price_from_last_file():
    avg_price = await get_avg_price_from_last_file()
    return (f"Средняя цена товара из последней таблицы: {avg_price}")