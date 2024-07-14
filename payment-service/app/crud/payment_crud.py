# app/crud/payment_crud.py

from sqlmodel import Session
from app.models.payment_model import Payment

def create_payment(payment: Payment, session: Session) -> Payment:
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment

def get_payment(payment_id: int, session: Session) -> Payment:
    return session.get(Payment, payment_id)
