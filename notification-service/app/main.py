# main.py

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Session
from app.models.notification_model import Notification
from app.crud.notification_crud import create_notification, get_notification
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
app = FastAPI(lifespan=lifespan, title="Notification Service", version="0.1.0")


@app.get("/")
def read_root():
    return {"Hello": "Mehjabeen Amir"}

@app.post("/notifications/", response_model=Notification)
def create_new_notification(notification: Notification, session: Session = Depends(get_session)):
    return create_notification(notification, session)

@app.get("/notifications/{notification_id}", response_model=Notification)
def get_single_notification(notification_id: int, session: Session = Depends(get_session)):
    notification = get_notification(notification_id, session)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification
