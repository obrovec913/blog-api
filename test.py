import httpx
import asyncio

BASE_URL = "http://localhost:8000"

async def register_user():
    response =  httpx.post(f"{BASE_URL}/register", json={"username": "testuser", "password": "password123"})
    print("Register User:", response)

async def login_user():
    response = httpx.post(f"{BASE_URL}/token", data={"username": "testuser", "password": "password123"})
    print("Login User:", response.json())
    return response.json().get("access_token")

async def create_post(access_token):
    response =  httpx.post(f"{BASE_URL}/posts", headers={"Authorization": f"Bearer {access_token}"}, json={"title": "My First Post", "content": "This is the content of my first post."})
    print("Create Post:", response.json())

async def read_posts():
    response =  httpx.get(f"{BASE_URL}/posts")
    print("Read Posts:", response.json())

async def read_post(post_id):
    response =  httpx.get(f"{BASE_URL}/post/{post_id}")
    print("Read Post:", response.json())

async def update_post(access_token, post_id):
    response =  httpx.put(f"{BASE_URL}/posts/{post_id}", headers={"Authorization": f"Bearer {access_token}"}, json={"title": "Updated Title", "content": "Updated content of the post."})
    print("Update Post:", response.json())

async def delete_post(access_token, post_id):
    response =  httpx.delete(f"{BASE_URL}/posts/{post_id}", headers={"Authorization": f"Bearer {access_token}"})
    print("Delete Post:", response.json())

async def search_posts(query):
    response =  httpx.get(f"{BASE_URL}/posts/search", params={"query": query})
    print("Search Posts:", response.json())

async def get_user_statistics(user_id):
    response =  httpx.get(f"{BASE_URL}/posts/statistics/{user_id}")
    print("User Statistics:", response.json())

async def main():
    await register_user()
    token = await login_user()
    await create_post(token)
    await read_posts()
    await read_post(1)  # Замените 1 на ID вашего поста
    await update_post(token, 1)  # Замените 1 на ID вашего поста
    await delete_post(token, 1)  # Замените 1 на ID вашего поста
    await search_posts("My First Post")
    await get_user_statistics(1)  # Замените 1 на ID пользователя

if __name__ == "__main__":
    asyncio.run(main())
