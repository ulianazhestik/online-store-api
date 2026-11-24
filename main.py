import time

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session

import models
import repository
from database import Base, engine, get_db
from schemas import (
    OrderCreate, OrderResponse, OrderUpdate, ProductCreate, ProductResponse,
    ProductUpdate, UserCreate, UserResponse, UserUpdate,
)

Base.metadata.create_all(engine)
app = FastAPI(title="Online store API")


@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.perf_counter() - start)
    return response


def require(db: Session, model, object_id: int):
    obj = repository.get_one(db, model, object_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    return obj


@app.post("/users", response_model=UserResponse)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    return repository.create(db, models.User, data.model_dump())


@app.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return repository.get_all(db, models.User)


@app.get("/users/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    return require(db, models.User, id)


@app.patch("/users/{id}", response_model=UserResponse)
def update_user(id: int, data: UserUpdate, db: Session = Depends(get_db)):
    return repository.update(db, require(db, models.User, id), data.model_dump(exclude_unset=True))


@app.delete("/users/{id}")
def delete_user(id: int, db: Session = Depends(get_db)):
    repository.delete(db, require(db, models.User, id))
    return {"message": "User deleted"}


@app.post("/products", response_model=ProductResponse)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    return repository.create(db, models.Product, data.model_dump())


@app.get("/products", response_model=list[ProductResponse])
def get_products(min_price: float | None = None, db: Session = Depends(get_db)):
    return repository.get_all(db, models.Product, min_price)


@app.get("/products/{id}", response_model=ProductResponse)
def get_product(id: int, db: Session = Depends(get_db)):
    return require(db, models.Product, id)


@app.patch("/products/{id}", response_model=ProductResponse)
def update_product(id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    return repository.update(db, require(db, models.Product, id), data.model_dump(exclude_unset=True))


@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    repository.delete(db, require(db, models.Product, id))
    return {"message": "Product deleted"}


def check_order_data(db: Session, user_id: int, items: list[dict]):
    require(db, models.User, user_id)
    for item in items:
        require(db, models.Product, item["product_id"])


@app.post("/orders", response_model=OrderResponse)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    values = data.model_dump()
    check_order_data(db, values["user_id"], values["items"])
    return repository.create_order(db, values["user_id"], values["items"])


@app.get("/orders", response_model=list[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    return repository.get_all(db, models.Order)


@app.get("/orders/{id}", response_model=OrderResponse)
def get_order(id: int, db: Session = Depends(get_db)):
    return require(db, models.Order, id)


@app.patch("/orders/{id}", response_model=OrderResponse)
def update_order(id: int, data: OrderUpdate, db: Session = Depends(get_db)):
    order = require(db, models.Order, id)
    values = data.model_dump(exclude_unset=True)
    if "user_id" in values:
        require(db, models.User, values["user_id"])
    if "items" in values:
        for item in values["items"]:
            require(db, models.Product, item["product_id"])
        repository.replace_order_items(db, order, values.pop("items"))
    return repository.update(db, order, values) if values else order


@app.delete("/orders/{id}")
def delete_order(id: int, db: Session = Depends(get_db)):
    repository.delete(db, require(db, models.Order, id))
    return {"message": "Order deleted"}
