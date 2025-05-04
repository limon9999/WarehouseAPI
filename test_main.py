"""
Тесты для API с использованием FastAPI TestClient.
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db
from models import User, Warehouse, Product

# Настройка тестовой базы данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Переопределяем зависимость get_db
def override_get_db():
    """
    Переопределение функции get_db для использования в тестах.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Подставляем тестовую базу данных
app.dependency_overrides[get_db] = override_get_db

# Создаем таблицы в тестовой базе данных
Base.metadata.create_all(bind=engine)

# Создаем клиент для тестирования
client = TestClient(app)


# Фикстура для тестовой базы данных
@pytest.fixture(autouse=True)
def setup_db():
    """
    Очистка базы данных перед каждым тестом.
    """
    # Настраиваем базу данных перед каждым тестом
    Base.metadata.create_all(bind=engine)
    
    # Выполняем тест
    yield
    
    # Очищаем базу данных после теста
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_register_user():
    """
    Тест регистрации пользователя.
    """
    response = client.post(
        "/register",
        json={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data


def test_register_duplicate_user():
    """
    Тест регистрации пользователя с дублирующимся именем.
    """
    # Регистрируем пользователя в первый раз
    client.post(
        "/register",
        json={"username": "testuser", "password": "testpassword"}
    )
    
    # Пытаемся зарегистрировать пользователя с тем же именем
    response = client.post(
        "/register",
        json={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 400
    assert "уже существует" in response.json()["detail"]


def test_login_user():
    """
    Тест аутентификации пользователя.
    """
    # Регистрируем пользователя
    client.post(
        "/register",
        json={"username": "loginuser", "password": "testpassword"}
    )
    
    # Входим в систему
    response = client.post(
        "/login",
        json={"username": "loginuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials():
    """
    Тест аутентификации с неверными учетными данными.
    """
    # Регистрируем пользователя
    client.post(
        "/register",
        json={"username": "loginuser", "password": "testpassword"}
    )
    
    # Пытаемся войти с неверным паролем
    response = client.post(
        "/login",
        json={"username": "loginuser", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert "Invalid credentials" in response.json()["detail"]


def test_create_warehouse():
    """
    Тест создания склада.
    """
    response = client.post(
        "/warehouses/",
        json={"name": "Test Warehouse", "location": "Test Location"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Warehouse"
    assert data["location"] == "Test Location"
    assert "id" in data
    assert data["products"] == []


def test_get_warehouses():
    """
    Тест получения списка складов.
    """
    # Создаем склад
    client.post(
        "/warehouses/",
        json={"name": "Test Warehouse 1", "location": "Test Location 1"}
    )
    client.post(
        "/warehouses/",
        json={"name": "Test Warehouse 2", "location": "Test Location 2"}
    )
    
    # Получаем список складов
    response = client.get("/warehouses/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Test Warehouse 1"
    assert data[1]["name"] == "Test Warehouse 2"


def test_get_warehouse():
    """
    Тест получения информации о складе.
    """
    # Создаем склад
    response = client.post(
        "/warehouses/",
        json={"name": "Test Warehouse", "location": "Test Location"}
    )
    warehouse_id = response.json()["id"]
    
    # Получаем информацию о складе
    response = client.get(f"/warehouses/{warehouse_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Warehouse"
    assert data["id"] == warehouse_id


def test_get_warehouse_not_found():
    """
    Тест получения информации о несуществующем складе.
    """
    response = client.get("/warehouses/999")
    assert response.status_code == 404
    assert "Склад не найден" in response.json()["detail"]


def test_create_product():
    """
    Тест создания продукта.
    """
    # Создаем склад
    warehouse_response = client.post(
        "/warehouses/",
        json={"name": "Product Test Warehouse", "location": "Test Location"}
    )
    warehouse_id = warehouse_response.json()["id"]
    
    # Создаем продукт
    response = client.post(
        "/products/",
        json={"name": "Test Product", "quantity": 10, "warehouse_id": warehouse_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["quantity"] == 10
    assert data["warehouse_id"] == warehouse_id


def test_create_product_warehouse_not_found():
    """
    Тест создания продукта с несуществующим складом.
    """
    response = client.post(
        "/products/",
        json={"name": "Test Product", "quantity": 10, "warehouse_id": 999}
    )
    assert response.status_code == 404
    assert "Склад не найден" in response.json()["detail"]


def test_get_products():
    """
    Тест получения списка продуктов.
    """
    # Создаем склад
    warehouse_response = client.post(
        "/warehouses/",
        json={"name": "Products Test Warehouse", "location": "Test Location"}
    )
    warehouse_id = warehouse_response.json()["id"]
    
    # Создаем продукты
    client.post(
        "/products/",
        json={"name": "Test Product 1", "quantity": 10, "warehouse_id": warehouse_id}
    )
    client.post(
        "/products/",
        json={"name": "Test Product 2", "quantity": 20, "warehouse_id": warehouse_id}
    )
    
    # Получаем список продуктов
    response = client.get("/products/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Test Product 1"
    assert data[1]["name"] == "Test Product 2"


def test_update_product():
    """
    Тест обновления информации о продукте.
    """
    # Создаем склад
    warehouse_response = client.post(
        "/warehouses/",
        json={"name": "Update Test Warehouse", "location": "Test Location"}
    )
    warehouse_id = warehouse_response.json()["id"]
    
    # Создаем продукт
    product_response = client.post(
        "/products/",
        json={"name": "Original Product", "quantity": 10, "warehouse_id": warehouse_id}
    )
    product_id = product_response.json()["id"]
    
    # Обновляем продукт
    response = client.put(
        f"/products/{product_id}",
        json={"name": "Updated Product", "quantity": 20, "warehouse_id": warehouse_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Product"
    assert data["quantity"] == 20


def test_update_product_not_found():
    """
    Тест обновления несуществующего продукта.
    """
    # Создаем склад для валидного warehouse_id
    warehouse_response = client.post(
        "/warehouses/",
        json={"name": "Update Test Warehouse", "location": "Test Location"}
    )
    warehouse_id = warehouse_response.json()["id"]
    
    response = client.put(
        "/products/999",
        json={"name": "Updated Product", "quantity": 20, "warehouse_id": warehouse_id}
    )
    assert response.status_code == 404
    assert "Продукт не найден" in response.json()["detail"]


def test_delete_product():
    """
    Тест удаления продукта.
    """
    # Создаем склад
    warehouse_response = client.post(
        "/warehouses/",
        json={"name": "Delete Test Warehouse", "location": "Test Location"}
    )
    warehouse_id = warehouse_response.json()["id"]
    
    # Создаем продукт
    product_response = client.post(
        "/products/",
        json={"name": "Delete Product", "quantity": 10, "warehouse_id": warehouse_id}
    )
    product_id = product_response.json()["id"]
    
    # Удаляем продукт
    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 200
    
    # Проверяем, что продукт удален
    products_response = client.get("/products/")
    assert len(products_response.json()) == 0


def test_delete_product_not_found():
    """
    Тест удаления несуществующего продукта.
    """
    response = client.delete("/products/999")
    assert response.status_code == 404
    assert "Продукт не найден" in response.json()["detail"] 