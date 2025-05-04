"""
Основной модуль приложения FastAPI.
Содержит определения маршрутов API и конфигурацию приложения.
"""
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

import uvicorn
import schemas
import crud
import models
from database import get_db, engine, Base

# Создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI()
security = HTTPBearer()

# Функция для получения текущего пользователя по токену
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    """
    Получение текущего пользователя из JWT токена.
    Используется для защиты маршрутов API с помощью Depends().
    """
    user = crud.get_user_from_token(db, credentials.credentials)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Неверный токен аутентификации",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserRegister, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя.
    """
    # Проверяем, существует ли пользователь с таким именем
    db_user = crud.create_user(db=db, user=user)
    if not db_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким именем уже существует"
        )
    return db_user


@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Аутентификация пользователя и выдача JWT токена.
    """
    db_user = crud.authenticate_user(db=db, username=user.username, password=user.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = crud.create_jwt_token(user=db_user)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/warehouses/", response_model=schemas.Warehouse)
def create_warehouse(
    warehouse: schemas.WarehouseCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создание нового склада.
    """
    return crud.create_warehouse(db=db, warehouse=warehouse)


@app.get("/warehouses/", response_model=list[schemas.Warehouse])
def get_warehouses(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение списка всех складов.
    """
    warehouses = db.query(models.Warehouse).all()
    return warehouses


@app.get("/warehouses/{warehouse_id}", response_model=schemas.Warehouse)
def get_warehouse(
    warehouse_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение информации о конкретном складе по его ID.
    """
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
    if warehouse is None:
        raise HTTPException(status_code=404, detail="Склад не найден")
    return warehouse


@app.post("/products/", response_model=schemas.Product)
def create_product(
    product: schemas.ProductCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создание нового продукта.
    """
    product = crud.create_product(db=db, product=product)
    if product is None:
        raise HTTPException(status_code=404, detail="Склад не найден")
    return product


@app.get("/products/", response_model=list[schemas.Product])
def get_products(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение списка всех продуктов.
    """
    products = db.query(models.Product).all()
    return products


@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    product: schemas.ProductCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновление информации о продукте.
    """
    db_product = crud.update_product(db=db, product_id=product_id, product=product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    return db_product


@app.delete("/products/{product_id}", response_model=schemas.Product)
def delete_product(
    product_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Удаление продукта.
    """
    db_product = crud.delete_product(db=db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    return db_product


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
