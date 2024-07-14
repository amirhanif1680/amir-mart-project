from sqlmodel import Session, select
from app.models.order_model import Order, OrderUpdate
from fastapi import HTTPException

def add_new_order(order_data: Order, session: Session) -> Order:
    session.add(order_data)
    session.commit()
    session.refresh(order_data)
    return order_data

def get_all_orders(session: Session) -> list[Order]:
    return session.exec(select(Order)).all()

def get_order_by_id(order_id: int, session: Session) -> Order:
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

def delete_order_by_id(order_id: int, session: Session) -> dict:
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    session.delete(order)
    session.commit()
    return {"detail": "Order deleted"}

def update_order_by_id(order_id: int, to_update_order_data: OrderUpdate, session: Session) -> Order:
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order_data = to_update_order_data.dict(exclude_unset=True)
    for key, value in order_data.items():
        setattr(order, key, value)
    session.add(order)
    session.commit()
    session.refresh(order)
    return order
