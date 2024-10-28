# app/user_operations.py
from .models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def get_user_by_username(db: AsyncSession, username: str):
     
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()