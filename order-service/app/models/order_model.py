from sqlmodel import SQLModel, Field
from typing import Optional

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int
    quantity: int
    price: float

class OrderUpdate(SQLModel):
    product_id: Optional[int]
    quantity: Optional[int]
    price: Optional[float]
