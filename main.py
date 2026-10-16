"""
نقطه ورود اصلی پروژه موتور برآورد
Estimation Engine - Main Entry Point

با نام و یاد خداوند مهربان
"""

import sys
import os

# اضافه کردن مسیر پروژه
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from estimation_engine.db.database import init_db
from estimation_engine.bot.telegram_bot import run_bot


def main():
    """نقطه ورود اصلی"""
    print("=" * 50)
    print("🏗️  Estimation Engine - موتور برآورد مصالح")
    print("=" * 50)
    print()

    # ۱. ایجاد دیتابیس
    print("📦 در حال ایجاد دیتابیس...")
    try:
        init_db()
        print("✅ دیتابیس آماده است.")
    except Exception as e:
        print(f"⚠️  خطا در ایجاد دیتابیس: {e}")

    print()

    # ۲. راه‌اندازی ربات تلگرام
    print("🤖 در حال راه‌اندازی ربات تلگرام...")
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n👋 ربات متوقف شد.")
    except Exception as e:
        print(f"❌ خطا در راه‌اندازی ربات: {e}")
        print("\n💡 لطفاً بررسی کنید:")
        print("   1. توکن ربات در فایل .env تنظیم شده باشد")
        print("   2. اتصال اینترنت فعال باشد")
        sys.exit(1)


if __name__ == "__main__":
    main()
