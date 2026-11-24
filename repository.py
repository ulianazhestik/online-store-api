from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Order, OrderItem, Product, User


def get_all(db: Session, model, min_price: float | None = None):
    statement = select(model)
    if model is Product and min_price is not None:
        statement = statement.where(Product.price >= min_price)
    return db.scalars(statement).all()


def get_one(db: Session, model, object_id: int):
    return db.get(model, object_id)


def create(db: Session, model, data: dict):
    obj = model(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, obj, data: dict):
    for key, value in data.items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, obj):
    db.delete(obj)
    db.commit()


def create_order(db: Session, user_id: int, items: list[dict]):
    order = Order(user_id=user_id)
    order.items = [OrderItem(**item) for item in items]
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def replace_order_items(db: Session, order: Order, items: list[dict]):
    order.items = [OrderItem(**item) for item in items]
    db.commit()
    db.refresh(order)
    return order
