import os

# Определение структуры проекта
project_structure = {
    
        "app": {
            "__init__.py": "",
            "main.py": """
from fastapi import FastAPI, HTTPException
from .schemas import Post, PostCreate
from .database import database
from . import crud

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/posts", response_model=list[Post])
async def read_posts():
    return await crud.get_posts()

@app.get("/posts/{post_id}", response_model=Post)
async def read_post(post_id: int):
    post = await crud.get_post(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.post("/posts", response_model=Post)
async def create_post(post: PostCreate):
    return await crud.create_post(post)

@app.put("/posts/{post_id}", response_model=Post)
async def update_post(post_id: int, post: PostCreate):
    await crud.update_post(post_id, post)
    return await crud.get_post(post_id)

@app.delete("/posts/{post_id}", response_model=dict)
async def delete_post(post_id: int):
    await crud.delete_post(post_id)
    return {"status": "Post deleted"}
            """,
            "models.py": """
from sqlalchemy import Table, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import metadata

posts = Table(
    "posts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("content", String, nullable=False),
    Column("created_at", DateTime, default=func.now()),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now())
)
            """,
            "schemas.py": """
from pydantic import BaseModel
from datetime import datetime

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
            """,
            "crud.py": """
from .models import posts
from .database import database
from .schemas import PostCreate

async def get_posts():
    query = posts.select()
    return await database.fetch_all(query)

async def get_post(post_id: int):
    query = posts.select().where(posts.c.id == post_id)
    return await database.fetch_one(query)

async def create_post(post: PostCreate):
    query = posts.insert().values(**post.dict())
    last_record_id = await database.execute(query)
    return {**post.dict(), "id": last_record_id}

async def update_post(post_id: int, post: PostCreate):
    query = posts.update().where(posts.c.id == post_id).values(**post.dict())
    await database.execute(query)

async def delete_post(post_id: int):
    query = posts.delete().where(posts.c.id == post_id)
    await database.execute(query)
            """,
            "database.py": """
from databases import Database
from sqlalchemy import create_engine, MetaData

DATABASE_URL = "postgresql+asyncpg://user:password@db/blog_db"

database = Database(DATABASE_URL)
metadata = MetaData()
            """,
            "config.py": "",
        },
        "Dockerfile": """
FROM python:3.10

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
        """,
        "docker-compose.yml": """
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: blog_db
    volumes:
      - ./data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    depends_on:
      - db
        """,
        "requirements.txt": """
fastapi
asyncpg
sqlalchemy
databases
pydantic
        """,
        "README.md": """
# Blog API

### Установка и запуск

1. Запустите `docker-compose`:
   ```bash
   docker-compose up -d --build
"""}


# Функция для создания структуры проекта
def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):  # Создание папок
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)  # Рекурсивное создание вложенных элементов
        else:  # Создание файлов
            with open(path, "w", encoding="utf-8") as f:
                f.write(content.strip())

# Запуск создания структуры проекта
create_structure(".", project_structure)
print("Проект успешно создан!")