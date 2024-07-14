from aiokafka import AIOKafkaConsumer
import asyncio
import json
from app.crud.notification_crud import create_notification
from app.models.notification_model import Notification
from app.deps import get_session

async def consume_messages(topic: str, bootstrap_servers: str):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="my-notification-consumer-group"
    )
    await consumer.start()
    try:
        async for message in consumer:
            notification_data = json.loads(message.value.decode())
            with next(get_session()) as session:
                await create_notification(Notification(**notification_data), session)
    finally:
        await consumer.stop()
