from app.models.notification_model import NotificationCreate

async def send_notification(notification: NotificationCreate) -> dict:
    # Simulate sending a notification
    response = {"status": "success", "message": f"Notification sent to {notification.recipient}"}
    return response
