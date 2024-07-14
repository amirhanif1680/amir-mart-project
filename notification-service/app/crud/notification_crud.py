# app/crud/notification_crud.py

from sqlmodel import Session
from app.models.notification_model import Notification

def create_notification(notification: Notification, session: Session) -> Notification:
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification

def get_notification(notification_id: int, session: Session) -> Notification:
    return session.get(Notification, notification_id)
