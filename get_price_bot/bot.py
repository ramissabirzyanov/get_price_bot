import os

from get_price_bot.parser import logger
from get_price_bot.utils import (
    read_excel_file,
    get_data_and_insert_to_db,
    avg_price_from_last_file
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ApplicationBuilder,
    CallbackQueryHandler
)


TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает полученный файл Excel.
    Сохраняет данные в БД.
    Выводит средний прайс.
    """
    try:
        await update.message.reply_text("Обработка файла. Это может занять несколько минут...")

        if not update.message.document.file_name.endswith('.xlsx'):
            await update.message.reply_text("Файл должен быть в формате Excel (.xlsx)")
            return

        os.makedirs('./uploaded_files', exist_ok=True)
        uploaded_file = update.message.document
        file = await context.bot.get_file(uploaded_file.file_id)
        file_path = f'./uploaded_files/{file.file_id}.xlsx'
        try:
            await file.download_to_drive(file_path)
        except TelegramError as e:
            logger.error(f"Ошибка при загрузке файла: {e}")
            await update.message.reply_text("Ошибка при загрузке файла.")
            return
        try:
            df = read_excel_file(file_path)
            table_str = df.to_string(index=False)
        except ValueError as e:
            await update.message.reply_text(e)
            return

        await update.message.reply_text(f"Cодержимое таблицы:\n\n{table_str}")
        await update.message.reply_text("Получаем данные цен, подождите пожалуйста")
        await update.message.reply_text(await get_data_and_insert_to_db(df))
        await update.message.reply_text(await avg_price_from_last_file())

    except TelegramError as e:
        logger.error(f"Ошибка обработки файла: {e}")
        await update.message.reply_text("Произошла ошибка при обработке файла")
        return
    except Exception as e:
        logger.critical(f"Неизвестная ошибка при чтении Excel: {e}")
        await update.message.reply_text("Произошла неизвестная ошибка, попробуйте позже")
        return

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение пользователю с инструкциями по загрузке файла."""

    keyboard = [
        [InlineKeyboardButton("Загрузить файл", callback_data='upload_file')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! Пожалуйста, загрузите файл Excel с информацией о сайтах для парсинга.\n\n"
        "Файл должен содержать следующие колонки:\n"
        "- `title`\n"
        "- `url`\n"
        "- `xpath`",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает нажатие кнопки."""
    query = update.callback_query
    await query.answer()

    if query.data == 'upload_file':
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Пожалуйста, нажмите 📎 и выберите файл для загрузки Excel файла."
        )
        context.user_data['awaiting_file'] = True


if __name__ == "__main__":
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()
