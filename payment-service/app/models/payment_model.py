# app/models/payment_model.py

from sqlmodel import SQLModel, Field
from typing import Optional

class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    order_id: int
    amount: float
    status: str
