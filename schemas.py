"""
Схемы данных Pydantic для валидации запросов и ответов.
"""
from typing import List

from pydantic import BaseModel


class UserRegister(BaseModel):
    """Схема для регистрации пользователя"""
    username: str
    password: str


class UserLogin(BaseModel):
    """Схема для входа пользователя в систему"""
    username: str
    password: str


class UserResponse(BaseModel):
    """Схема для ответа с информацией о пользователе"""
    id: int
    username: str

    class Config:
        """Настройки Pydantic модели"""
        from_attributes = True


class ProductBase(BaseModel):
    """Базовая схема продукта"""
    name: str
    quantity: int
    warehouse_id: int


class Product(ProductBase):
    """Схема продукта с id"""
    id: int

    class Config:
        """Настройки Pydantic модели"""
        from_attributes = True


class ProductCreate(ProductBase):
    """Схема для создания продукта"""
    pass


class WarehouseBase(BaseModel):
    """Базовая схема склада"""
    name: str
    location: str


class WarehouseCreate(WarehouseBase):
    """Схема для создания склада"""
    pass


class Warehouse(WarehouseBase):
    """Схема склада с id и списком продуктов"""
    id: int
    products: List[Product] = []

    class Config:
        """Настройки Pydantic модели"""
        from_attributes = True

