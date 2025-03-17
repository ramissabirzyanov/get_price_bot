import pandas as pd
from get_price_bot.parser import get_price, logger
from get_price_bot.db import insert_data_to_db
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, ApplicationBuilder
import os
import asyncio


TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает полученный файл Excel."""

    try:
        await update.message.reply_text("Обработка файла. Это может занять несколько минут...")

        if not update.message.document.file_name.endswith('.xlsx'):
            await update.message.reply_text("Файл должен быть в формате Excel (.xlsx)")

        os.makedirs('./uploaded_files', exist_ok=True)

        uploaded_file = update.message.document
        file = await context.bot.get_file(uploaded_file.file_id)
        file_path = f'./uploaded_files/{file.file_id}.xlsx'
        try:
            await file.download_to_drive(file_path)
        except TelegramError as e:
            logger.error(f"Ошибка при загрузке файла: {str(e)}")
            await update.message.reply_text("Ошибка при загрузке файла.")
            return
        df = pd.read_excel(file_path)

    except TelegramError as e:
        logger.error(f"Ошибка обработки файла: {str(e)}")
        await update.message.reply_text("Произошла ошибка при обработке файла")
        return

    required_columns = ['title', 'url', 'xpath']
    if not all(col in df.columns for col in required_columns):
        await update.message.reply_text("Ошибка! Файл должен содержать колонки: title, url, xpath.")
        return

    data_to_insert = []

    for row in df.itertuples(index=False):
        title = row.title
        url = row.url
        xpath = row.xpath
        price = get_price(url, xpath)
        data_to_insert.append((title, url, xpath, price))

    insert_data_to_db(data_to_insert)
    await update.message.reply_text("Файл успешно загружен и данные добавлены в базу данных.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение пользователю с инструкциями по загрузке файла."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! Пожалуйста, загрузите файл Excel с информацией о сайтах для парсинга.\n\n"
        "Файл должен содержать следующие колонки:\n"
        "- `title`\n"
        "- `url`\n"
        "- `xpath`",
        parse_mode="Markdown"
    )


async def main() -> None:
    """Запуск бота."""
    application = ApplicationBuilder().token("YOUR_BOT_API_KEY").build()

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)
    application.add_handler(MessageHandler(filters.Document.XLSX, handle_file))
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
