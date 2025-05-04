"""
Модуль для настройки базы данных SQLAlchemy.
Создает подключение к базе данных и сессии.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Генератор сессий базы данных для использования с FastAPI Depends().
    Обеспечивает создание и закрытие сессии базы данных.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Импортировать модели для создания таблиц
# Не используется напрямую, но необходимо для создания таблиц в main.py
# from models import User, Warehouse, Product
