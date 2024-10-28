from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime
from fastapi import HTTPException, status
from .models import Post, User
from .schemas import PostCreate, UserCreate
from .auth import get_password_hash
from .user_operations import get_user_by_username

# Получение списка постов с пагинацией
async def get_posts(db: AsyncSession, skip: int = 0, limit: int = 10):
    try:
        query = select(Post)
        
        # Если указаны skip или limit, применяем их для пагинации
        if skip or limit:
            query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        posts = result.scalars().all()

        if not posts:
            raise HTTPException(status_code=404, detail="No posts found")

        return posts

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching posts: {str(e)}")


# Получение одного поста по ID
async def get_post(db: AsyncSession, post_id: int):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# Создание нового поста
async def create_post(db: AsyncSession, post: PostCreate, user_id: int):
    try:
        db_post = Post(**post.model_dump(), user_id=user_id)
        db.add(db_post)
        await db.commit()
        await db.refresh(db_post)
        return db_post
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating post: {str(e)}")

# Обновление поста
async def update_post(db: AsyncSession, post_id: int, post_data: PostCreate, ):
    result = await db.execute(select(Post).where(Post.id == post_id))
    db_post = result.scalar_one_or_none()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    try:
        for key, value in post_data.model_dump().items():
            setattr(db_post, key, value)
        await db.commit()
        await db.refresh(db_post)
        return db_post
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating post: {str(e)}")

# Удаление поста 
async def delete_post(db: AsyncSession, post_id: int, ):
    result = await db.execute(select(Post).where(Post.id == post_id))
    db_post = result.scalar_one_or_none()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    try:
        await db.delete(db_post)
        await db.commit()
        return {"message": "Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting post: {str(e)}")

# Поиск постов по названию или содержимому
async def search_posts(db: AsyncSession, query: str, skip: int = 0, limit: int = 10):
    try:
        search_query = select(Post).where(
            Post.title.ilike(f"%{query}%") | Post.content.ilike(f"%{query}%")
        ).offset(skip).limit(limit)
        result = await db.execute(search_query)
        posts = result.scalars().all()
        if not posts:
            raise HTTPException(status_code=404, detail="No posts found matching the search criteria")
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching posts: {str(e)}")

# Получение статистики по постам пользователя за текущий месяц
async def get_user_post_statistics(db: AsyncSession, user_id: int):
    try:
        current_date = datetime.now()
        query = select(
            func.count(Post.id).label("post_count")
        ).where(
            Post.user_id == user_id,
            Post.created_at >= current_date.replace(day=1)
        )
        result = await db.execute(query)
        post_count = result.scalar_one_or_none() or 0
        return {"average_posts_per_month": post_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user statistics: {str(e)}")

# Создание пользователя
async def create_user(db: AsyncSession, user: UserCreate):
    db_user = await get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=407, detail="Username already registered")
    try:
        hashed_password = get_password_hash(user.password)
        db_user = User(username=user.username, hashed_password=hashed_password)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except Exception as e:
        print("Register User:", e)
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")
