"""
Модели данных для приложения.
Определяет структуру таблиц базы данных.
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    """
    Модель пользователя для хранения информации об учетных записях пользователей.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class Warehouse(Base):
    """
    Модель склада для хранения информации о складах.
    """
    __tablename__ = 'warehouses'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String, nullable=True)

    products = relationship("Product", back_populates="warehouse")

class Product(Base):
    """
    Модель продукта для хранения информации о товарах на складе.
    """
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(Integer)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))

    warehouse = relationship("Warehouse", back_populates="products")