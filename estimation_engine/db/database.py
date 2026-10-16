"""
اتصال و مدیریت دیتابیس
Database Connection Manager
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base

# SQLite برای شروع
DATABASE_URL = "sqlite:///./estimation_engine.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # برای SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """ایجاد جداول دیتابیس"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """دریافت session دیتابیس"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
