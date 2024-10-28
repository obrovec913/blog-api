import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.main import app  # импорт приложения
from app.database import get_db
from app.models import Base


DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


import pytest_asyncio

@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        return db_session  # Возвращаем сессию напрямую, 

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield client
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)



from app.schemas import PostCreate, UserCreate

@pytest.mark.asyncio
async def test_create_post(client, db_session):
    # Создаём пользователя для авторизации
    user_data = {"username": "testuser", "password": "testpass"}
    await client.post("/register", json=user_data)

    # Получаем токен
    token_response = await client.post("/token", data=user_data)
    token = token_response.json()["access_token"]

    # Данные для создания поста
    post_data = {"title": "Test Post", "content": "This is a test post."}

    # Создание поста
    response = await client.post(
        "/posts",
        json=post_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    post = response.json()
    assert post["title"] == post_data["title"]
    assert post["content"] == post_data["content"]
    assert "id" in post  # Проверяем, что ID поста создан



@pytest.mark.asyncio
async def test_read_posts(client, db_session):
    user_data = {"username": "testuser", "password": "testpass"}
    await client.post("/register", json=user_data)

    # Получаем токен
    token_response = await client.post("/token", data=user_data)
    token = token_response.json()["access_token"]



    # Создаём несколько постов для теста
    post_data = [
        {"title": "Post 1", "content": "Content for post 1"},
        {"title": "Post 2", "content": "Content for post 2"},
        {"title": "Post 3", "content": "Content for post 3"}
    ]
    
    for data in post_data:
        await client.post("/posts", json=data, headers={"Authorization": f"Bearer {token}"})

    # Тест 1: Проверка возвращения всех постов, если пагинация не указана
    response = await client.get("/posts")
    assert response.status_code == 200
    posts = response.json()
    assert isinstance(posts, list)
    assert len(posts) == len(post_data)
    assert posts[0]["title"] == post_data[0]["title"]

    # Тест 2: Проверка пагинации с параметрами skip и limit
    skip, limit = 1, 1
    response_paginated = await client.get(f"/posts?skip={skip}&limit={limit}")
    assert response_paginated.status_code == 200
    paginated_posts = response_paginated.json()
    assert isinstance(paginated_posts, list)
    assert len(paginated_posts) == limit
    assert paginated_posts[0]["title"] == post_data[skip]["title"]


@pytest.mark.asyncio
async def test_read_post(client, db_session):
    # Создаём пользователя и пост для чтения
    user_data = {"username": "testuser", "password": "testpass"}
    await client.post("/register", json=user_data)

    token_response = await client.post("/token", data=user_data)
    token = token_response.json()["access_token"]

    post_data = {"title": "Test Post", "content": "This is a test post."}
    create_response = await client.post(
        "/posts",
        json=post_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    post_id = create_response.json()["id"]

    # Читаем пост по ID
    response = await client.get(f"/post/{post_id}")
    assert response.status_code == 200
    post = response.json()
    assert post["id"] == post_id
    assert post["title"] == post_data["title"]


@pytest.mark.asyncio
async def test_update_post(client, db_session):
    # Создаём пользователя и пост для обновления
    user_data = {"username": "testuser", "password": "testpass"}
    await client.post("/register", json=user_data)

    token_response = await client.post("/token", data=user_data)
    token = token_response.json()["access_token"]

    post_data = {"title": "Test Post", "content": "This is a test post."}
    create_response = await client.post(
        "/posts",
        json=post_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    post_id = create_response.json()["id"]

    # Данные для обновления поста
    updated_post_data = {"title": "Updated Post", "content": "This is an updated test post."}

    # Обновляем пост
    response = await client.put(
        f"/posts/{post_id}",
        json=updated_post_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    updated_post = response.json()
    assert updated_post["title"] == updated_post_data["title"]
    assert updated_post["content"] == updated_post_data["content"]


@pytest.mark.asyncio
async def test_delete_post(client, db_session):
    # Создаём пользователя и пост для удаления
    user_data = {"username": "testuser", "password": "testpass"}
    await client.post("/register", json=user_data)

    token_response = await client.post("/token", data=user_data)
    token = token_response.json()["access_token"]

    post_data = {"title": "Test Post", "content": "This is a test post."}
    create_response = await client.post(
        "/posts",
        json=post_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    post_id = create_response.json()["id"]

    # Удаляем пост
    response = await client.delete(f"/posts/{post_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Post deleted successfully"

    # Проверяем, что пост действительно удалён
    response = await client.get(f"/post/{post_id}")
    assert response.status_code == 404  # Пост должен быть не найден


@pytest.mark.asyncio
async def test_search_posts(client, db_session):
    # Создаём пользователя и несколько постов для поиска
    user_data = {"username": "testuser", "password": "testpass"}
    await client.post("/register", json=user_data)

    token_response = await client.post("/token", data=user_data)
    token = token_response.json()["access_token"]

    await client.post(
        "/posts",
        json={"title": "First Post", "content": "Content of the first post."},
        headers={"Authorization": f"Bearer {token}"}
    )
    await client.post(
        "/posts",
        json={"title": "Second Post", "content": "Content of the second post."},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Поиск постов
    response = await client.get("/posts/search?query=First")
    assert response.status_code == 200
    posts = response.json()
    assert len(posts) > 0
    assert posts[0]["title"] == "First Post"

