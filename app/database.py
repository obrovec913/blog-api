from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
import os
from .config import DATABASE_URL as url_db


DATABASE_URL = os.getenv("DATABASE_URL", url_db)

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal =  sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

Base = declarative_base()

# Функция для получения сессии
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
