"""
نقطه ورود ربات تلگرام
Telegram Bot Entry Point
"""

import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from estimation_engine.bot.handlers import (
    start_command,
    help_command,
    handle_text_message,
    handle_voice_message,
    error_handler,
)


def create_application(token: str = None) -> Application:
    """ساخت اپلیکیشن ربات تلگرام"""

    if not token:
        token = os.getenv("BOT_TOKEN", "")

    if not token:
        raise ValueError(
            "توکن ربات تنظیم نشده است.\n"
            "لطفاً BOT_TOKEN را در فایل .env تنظیم کنید."
        )

    application = Application.builder().token(token).build()

    # ثبت هندلرها
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # پیام متنی
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message)
    )

    # پیام صوتی (برای آینده)
    application.add_handler(
        MessageHandler(filters.VOICE, handle_voice_message)
    )

    # هندلر خطا
    application.add_error_handler(error_handler)

    return application


def run_bot():
    """اجرای ربات (Polling)"""
    print("🚀 در حال راه‌اندازی ربات...")
    application = create_application()
    print("✅ ربات فعال شد. Ctrl+C برای توقف.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    run_bot()
