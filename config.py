"""
Конфигурационный модуль для приложения.
Содержит настройки безопасности и другие константы.
"""
import os
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Добавляем значение по умолчанию, если переменная окружения не установлена
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_super_secret_key_for_jwt_encoding_keep_it_safe")
ALGORITHM = "HS256"