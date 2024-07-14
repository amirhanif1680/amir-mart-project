from contextlib import asynccontextmanager
import email
from typing import Annotated
from sqlmodel import Session, SQLModel
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json

from app import settings
from app.db_engine import engine
from app.models.user_model import User, UserUpdate
from app.crud.user_crud import add_new_user, get_all_users, get_user_by_id, delete_user_by_id, update_user_by_id
from app.deps import get_session, get_kafka_producer
from app.consumers.user_consumer import consume_messages
from app.hello_ai import chat_completion

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

async def consume_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="my-user-consumer-group",
    ) 
    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print("RAW")
            print(f"Received message on topic {message.topic}")
            user_data = json.loads(message.value.decode())
            print("TYPE", (type(user_data)))
            print(f"User Data {user_data}")
            
            with next(get_session()) as session:
                print("SAVING DATA TO DATABASE")
                db_insert_user = add_new_user(
                    user_data=User(**user_data), session=session)
                print("DB_INSERT_USER", db_insert_user)         
    finally:
        await consumer.stop()
                      
                  
# The first part of the function, before the yield, will
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating ... ... ?? !!! ")

    task = asyncio.create_task(consume_messages("USER", 'broker:19092'))
    create_db_and_tables()
    print("Startup Completed")
    
    yield


app = FastAPI(
    lifespan=lifespan,
    title="User Service API",
    version="0.0.1",
)


@app.get("/")
def read_root():
    return {"Hello": "Ayyan Amir"}


@app.post("/manage-users/", response_model=User)
async def create_new_user(user: User, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    """ Create a new user and send it to Kafka"""

    user_dict = {field: getattr(user, field) for field in user.dict()}
    user_json = json.dumps(user_dict).encode("utf-8")
    print("user_JSON:", user_json)
    # Produce message
    await producer.send_and_wait("USER", user_json)
    # new_user = add_new_user(user, session)
    return user


@app.get("/manage-users/all", response_model=list[User])
def call_all_users(session: Annotated[Session, Depends(get_session)]):
    """ Get all users from the database"""
    return get_all_users(session)


@app.get("/manage-users/{user_id}", response_model=User)
def get_single_user(user_id: int, session: Annotated[Session, Depends(get_session)]):
    """ Get a single user by ID"""
    try:
        return get_user_by_id(user_id=user_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/manage-users/{user_id}", response_model=dict)
def delete_single_user(user_id: int, session: Annotated[Session, Depends(get_session)]):
    """ Delete a single user by ID"""
    try:
        return delete_user_by_id(user_id=user_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/manage-users/{user_id}", response_model=User)
def update_single_user(user_id: int, user: UserUpdate, session: Annotated[Session, Depends(get_session)]):
    """ Update a single user by ID"""
    try:
        return update_user_by_id(user_id=user_id, to_update_user_data=user, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/hello-ai")
def get_ai_response(prompt: str):
    return chat_completion(prompt)
