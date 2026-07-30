import logging

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


# ============================================================
# НАСТРОЙКИ
# ============================================================

# Вставь сюда новый токен от BotFather
BOT_TOKEN = "8612691062:AAF3LL22m5ni_-reIH-yTzpFq1mOfVGto2k"

# ID канала «Фото со свадьбы»
ALBUM_CHANNEL_ID = -1003658758303


# ============================================================
# ЛОГИ
# ============================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# ============================================================
# КНОПКА
# ============================================================

keyboard = ReplyKeyboardMarkup(
    [
        ["📷 Отправить фото"],
    ],
    resize_keyboard=True,
)


# ============================================================
# КОМАНДА /START
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    message = update.effective_message

    if message is None:
        return

    text = (
        "💍 Добро пожаловать в свадебную фотогалерею!\n\n"
        "Отправляйте сюда фотографии со свадьбы.\n\n"
        "Можно сделать новый снимок или выбрать фотографию "
        "из галереи телефона.\n\n"
        "Все фотографии попадут в общий свадебный альбом."
    )

    await message.reply_text(
        text,
        reply_markup=keyboard,
    )


# ============================================================
# ИНСТРУКЦИЯ ПО ОТПРАВКЕ ФОТО
# ============================================================

async def send_photo_instruction(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    message = update.effective_message

    if message is None:
        return

    text = (
        "📷 Нажмите на значок скрепки 📎 рядом с полем ввода.\n\n"
        "Выберите «Камера», чтобы сделать новый снимок, "
        "или «Галерея», чтобы выбрать готовую фотографию.\n\n"
        "Можно отправлять сразу несколько фотографий."
    )

    await message.reply_text(
        text,
        reply_markup=keyboard,
    )


# ============================================================
# ПОДПИСЬ К ФОТО
# ============================================================

def get_sender_caption(update: Update, media_type: str) -> str:
    user = update.effective_user

    if user is None:
        return media_type

    if user.username:
        return (
            f"{media_type} от {user.full_name}\n"
            f"Пользователь: @{user.username}"
        )

    return f"{media_type} от {user.full_name}"


# ============================================================
# ОБРАБОТКА ОБЫЧНЫХ ФОТО
# ============================================================

async def photo_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    message = update.effective_message

    if message is None or not message.photo:
        return

    photo = message.photo[-1]
    caption = get_sender_caption(update, "📷 Фото")

    try:
        await context.bot.send_photo(
            chat_id=ALBUM_CHANNEL_ID,
            photo=photo.file_id,
            caption=caption,
        )

        await message.reply_text(
            "✅ Фотография добавлена в свадебный альбом!",
            reply_markup=keyboard,
        )

    except Exception as error:
        logger.exception(
            "Ошибка при отправке фото в канал: %s",
            error,
        )

        await message.reply_text(
            "❌ Не удалось добавить фотографию.\n"
            "Попробуйте отправить её ещё раз.",
            reply_markup=keyboard,
        )


# ============================================================
# ОБРАБОТКА ФОТО, ОТПРАВЛЕННЫХ КАК ФАЙЛ
# ============================================================

async def document_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    message = update.effective_message

    if message is None or message.document is None:
        return

    document = message.document
    mime_type = document.mime_type or ""

    if not mime_type.startswith("image/"):
        await message.reply_text(
            "Пожалуйста, отправьте фотографию.",
            reply_markup=keyboard,
        )
        return

    caption = get_sender_caption(
        update,
        "🖼 Фото в оригинальном качестве",
    )

    try:
        await context.bot.send_document(
            chat_id=ALBUM_CHANNEL_ID,
            document=document.file_id,
            caption=caption,
        )

        await message.reply_text(
            "✅ Фотография добавлена в свадебный альбом!",
            reply_markup=keyboard,
        )

    except Exception as error:
        logger.exception(
            "Ошибка при отправке файла в канал: %s",
            error,
        )

        await message.reply_text(
            "❌ Не удалось добавить фотографию.\n"
            "Попробуйте отправить её ещё раз.",
            reply_markup=keyboard,
        )


# ============================================================
# ОБРАБОТКА КНОПКИ И ТЕКСТА
# ============================================================

async def text_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    message = update.effective_message

    if message is None or message.text is None:
        return

    if message.text == "📷 Отправить фото":
        await send_photo_instruction(update, context)
        return

    await message.reply_text(
        "Отправьте фотографию через значок скрепки 📎.",
        reply_markup=keyboard,
    )


# ============================================================
# ОБРАБОТКА ОШИБОК
# ============================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    logger.exception(
        "Во время обработки обновления произошла ошибка",
        exc_info=context.error,
    )


# ============================================================
# ЗАПУСК БОТА
# ============================================================

def main() -> None:
    if BOT_TOKEN == "ВСТАВЬ_СЮДА_ТОКЕН":
        raise ValueError(
            "Вставь токен от BotFather в переменную BOT_TOKEN"
        )

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(
        CommandHandler(
            "start",
            start,
            filters=filters.ChatType.PRIVATE,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.PHOTO & filters.ChatType.PRIVATE,
            photo_handler,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Document.ALL & filters.ChatType.PRIVATE,
            document_handler,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND
            & filters.ChatType.PRIVATE,
            text_handler,
        )
    )

    application.add_error_handler(error_handler)

    print("Свадебный бот запущен")

    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()