"""
تنظیمات پروژه موتور برآورد
Estimation Engine Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """تنظیمات اصلی پروژه"""

    # Project
    PROJECT_NAME = "Estimation Engine"
    VERSION = "0.1.0"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./estimation_engine.db"
    )

    # Telegram Bot
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")

    # AI / LLM
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    USE_AI = os.getenv("USE_AI", "false").lower() == "true"

    # API
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))

    # Estimation Settings
    DEFAULT_WASTE_FACTOR = 1.10  # 10% ضایعات
    CONFIDENCE_THRESHOLD = 0.75   # حداقل اطمینان AI


settings = Settings()
