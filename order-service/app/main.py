from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session, SQLModel
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json

from app import settings
from app.db_engine import engine
from app.models.order_model import Order, OrderUpdate
from app.crud.order_crud import add_new_order, get_all_orders, get_order_by_id, delete_order_by_id, update_order_by_id
from app.deps import get_session, get_kafka_producer
from app.consumers.order_consumer import consume_messages
from app.hello_ai import chat_completion

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

async def consume_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
    topic,
    bootstrap_servers=bootstrap_servers,
    group_id="my-order-consumer-group",
    ) 
        # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print("RAW")
            print(f"Received message on topic {message.topic}")
            order_data = json.loads(message.value.decode())
            print("TYPE", (type(order_data)))
            print(f"Order Data {order_data}")
            
            with next(get_session()) as session:
                print("SAVING DATA TO DATABASE")
                db_insert_order = add_new_order(
                    order_data=Order(**order_data), session=session)
                print("DB_INSERT_ORDER", db_insert_order)         
    finally:
        await consumer.stop()
                      
                  
# The first part of the function, before the yield, will
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating ... ... ?? !!! ")

    task = asyncio.create_task(consume_messages("ORDER",'broker:19092'))
    create_db_and_tables()
    print("Startup Completed")
    
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Order Service API",
    version="0.0.1",
)


@app.get("/")
def read_root():
    return {"Hello": "Ayyan Sahib"}


@app.post("/manage-orders/", response_model=Order)
async def create_new_order(order: Order, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    """ Create a new order and send it to Kafka"""

    order_dict = {field: getattr(order, field) for field in order.dict()}
    order_json = json.dumps(order_dict).encode("utf-8")
    print("order_JSON:", order_json)
    # Produce message
    await producer.send_and_wait("ORDER", order_json)
    # new_order = add_new_order(order, session)
    return order


@app.get("/manage-orders/all", response_model=list[Order])
def call_all_orders(session: Annotated[Session, Depends(get_session)]):
    """ Get all orders from the database"""
    return get_all_orders(session)


@app.get("/manage-orders/{order_id}", response_model=Order)
def get_single_order(order_id: int, session: Annotated[Session, Depends(get_session)]):
    """ Get a single order by ID"""
    try:
        return get_order_by_id(order_id=order_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/manage-orders/{order_id}", response_model=dict)
def delete_single_order(order_id: int, session: Annotated[Session, Depends(get_session)]):
    """ Delete a single order by ID"""
    try:
        return delete_order_by_id(order_id=order_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/manage-orders/{order_id}", response_model=Order)
def update_single_order(order_id: int, order: OrderUpdate, session: Annotated[Session, Depends(get_session)]):
    """ Update a single order by ID"""
    try:
        return update_order_by_id(order_id=order_id, to_update_order_data=order, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/hello-ai")
def get_ai_response(prompt:str):
    return chat_completion(prompt)
