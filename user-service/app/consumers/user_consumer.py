from aiokafka import AIOKafkaConsumer
import asyncio
import json
from app.crud.user_crud import add_new_user
from app.models.user_model import User
from app.deps import get_session

async def consume_messages(topic: str, bootstrap_servers: str):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="my-user-consumer-group"
    )
    await consumer.start()
    try:
        async for message in consumer:
            print(f"Received message: {message.value.decode()}")
            user_data = json.loads(message.value.decode())
            with next(get_session()) as session:
                await add_new_user(User(**user_data), session)
    finally:
        await consumer.stop()
