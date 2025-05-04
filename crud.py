"""
Модуль для работы с базой данных.
Содержит функции для выполнения операций CRUD (Create, Read, Update, Delete).
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import jwt
from jwt.exceptions import InvalidTokenError

from config import pwd_context, SECRET_KEY, ALGORITHM
from schemas import UserRegister, WarehouseCreate, ProductCreate
from models import User, Warehouse, Product


def get_user_by_username(db: Session, username: str):
    """
    Получение пользователя по имени пользователя.
    """
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: UserRegister):
    """
    Создание нового пользователя.
    Проверяет существование пользователя и возвращает None, если пользователь уже существует.
    """
    # Проверяем, существует ли пользователь с таким именем
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        return None  # Пользователь уже существует
    
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, password=hashed_password)
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        return None  # Обработка случая, если произошла ошибка уникальности


def authenticate_user(db: Session, username: str, password: str):
    """
    Аутентификация пользователя по имени пользователя и паролю.
    """
    user = db.query(User).filter(User.username == username).first()
    if user and pwd_context.verify(password, user.password):
        return user
    return None


def create_jwt_token(user: User):
    """
    Создание JWT токена для аутентифицированного пользователя.
    """
    token = jwt.encode({"sub": user.username}, SECRET_KEY, algorithm=ALGORITHM)
    return token


def get_user_from_token(db: Session, token: str):
    """
    Получение пользователя из JWT токена.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return None
        return get_user_by_username(db, username=username)
    except InvalidTokenError:
        return None


def create_warehouse(db: Session, warehouse: WarehouseCreate):
    """
    Создание нового склада.
    """
    db_warehouse = Warehouse(**warehouse.dict())
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


def create_product(db: Session, product: ProductCreate):
    """
    Создание нового продукта.
    Проверяет существование склада и возвращает None, если склад не найден.
    """
    # Проверяем, существует ли склад с таким id
    warehouse = db.query(Warehouse).filter(Warehouse.id == product.warehouse_id).first()
    if warehouse is None:
        return None
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product: ProductCreate):
    """
    Обновление информации о продукте.
    """
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        return None
    db_product.name = product.name
    db_product.quantity = product.quantity
    db_product.warehouse_id = product.warehouse_id
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int):
    """
    Удаление продукта.
    """
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        return None
    db.delete(db_product)
    db.commit()
    return db_product

