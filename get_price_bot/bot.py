import pandas as pd
from get_price_bot.parser import get_price
from get_price_bot.db import insert_data_to_db
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import os


if not os.path.exists('./uploaded_excel_files'):
    os.makedirs('./uploaded_excel_files')



def handle_file(file_path):
    """Обрабатывает Excel файл, извлекает данные и сохраняет их в БД."""
    df = pd.read_excel(file_path)
    data_to_insert = []

    for index, row in df.iterrows():
        price = get_price(row['url'], row['xpath'])
        if price is not None:
            data_to_insert.append((row['title'], row['url'], row['xpath'], price))

    insert_data_to_db(data_to_insert)


def start(update: Update, context: CallbackContext) -> int:
    """Стартовая команда для бота."""
    update.message.reply_text('Привет! Отправьте мне файл Excel с данными для парсинга.')
