from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import HTTPException
from app.models.user_model import User, UserCreate, UserUpdate

async def add_new_user(user_data: UserCreate, session: AsyncSession) -> User:
    new_user = User.from_orm(user_data)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

async def get_all_users(session: AsyncSession) -> list[User]:
    result = await session.execute(select(User))
    return result.scalars().all()

async def get_user_by_id(user_id: int, session: AsyncSession) -> User:
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def delete_user_by_id(user_id: int, session: AsyncSession) -> dict:
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await session.delete(user)
    await session.commit()
    return {"message": "User deleted successfully"}

async def update_user_by_id(user_id: int, to_update_user_data: UserUpdate, session: AsyncSession) -> User:
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in to_update_user_data.dict(exclude_unset=True).items():
        setattr(user, key, value)

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
