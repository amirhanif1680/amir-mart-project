from aiokafka import AIOKafkaConsumer
import json

async def consume_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="my-order-consumer-group",
    ) 
    await consumer.start()
    try:
        async for message in consumer:
            print("RAW")
            print(f"Received message on topic {message.topic}")
            order_data = json.loads(message.value.decode())
            print("TYPE", (type(order_data)))
            print(f"Order Data {order_data}")
            
            # Implement your logic for processing the order data
    finally:
        await consumer.stop()
