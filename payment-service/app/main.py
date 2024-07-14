# main.py

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Session
from app.models.payment_model import Payment
from app.crud.payment_crud import create_payment, get_payment
from app.deps import get_session
from app.db_engine import engine

# Create the database and tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Context manager for lifespan
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    create_db_and_tables()
    yield

# Initialize the FastAPI app
app = FastAPI(lifespan=lifespan, title="Payment Service", version="0.1.0")

@app.get("/")
def read_root():
    return {"Hello": "Shah Gee"}

@app.post("/payments/", response_model=Payment)
def create_new_payment(payment: Payment, session: Session = Depends(get_session)):
    return create_payment(payment, session)

@app.get("/payments/{payment_id}", response_model=Payment)
def get_single_payment(payment_id: int, session: Session = Depends(get_session)):
    payment = get_payment(payment_id, session)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
