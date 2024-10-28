from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from .database import get_db, startup_event
from .crud import (
    create_post as crud_create_post,
    get_posts as crud_get_posts,
    get_post as crud_get_post,
    update_post as crud_update_post,
    delete_post as crud_delete_post,
    search_posts as crud_search_posts,
    get_user_post_statistics as crud_get_user_post_statistics,
    create_user,
)
from .schemas import PostCreate, Post, User, UserCreate, Token
from .auth import get_current_user, create_access_token, authenticate_user
from .user_operations import get_user_by_username

app = FastAPI()

app.add_event_handler("startup", startup_event)


@app.get("/posts", response_model=list[Post])
async def read_posts(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    if skip or limit:
        posts = await crud_get_posts(db, skip=skip, limit=limit)
    else:
        posts = await crud_get_posts(db)
    if not posts:
        raise HTTPException(status_code=404, detail="No posts found")
    return posts

@app.get("/post/{id}", response_model=Post)
async def read_post(id: int, db: AsyncSession = Depends(get_db)):
    post = await crud_get_post(db, id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.post("/posts", response_model=Post)
async def create_post(post: PostCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return await crud_create_post(db, post, user_id=current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error creating post") from e

@app.put("/posts/{id}", response_model=Post)
async def update_post(id: int, post: PostCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing_post = await crud_get_post(db, id)
    if not existing_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if existing_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    
    try:
        return await crud_update_post(db, id, post)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error updating post") from e

@app.delete("/posts/{id}")
async def delete_post(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = await crud_get_post(db, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    try:
        await crud_delete_post(db, id)
        return {"message": "Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error deleting post") from e

@app.get("/posts/search", response_model=list[Post])
async def search_posts(query: str, skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    posts = await crud_search_posts(db, query=query, skip=skip, limit=limit)
    if not posts:
        raise HTTPException(status_code=404, detail="No posts found matching the search criteria")
    return posts

@app.get("/posts/statistics/{user_id}")
async def get_user_statistics(user_id: int, db: AsyncSession = Depends(get_db)):
    statistics = await crud_get_user_post_statistics(db, user_id)
    if not statistics:
        raise HTTPException(status_code=404, detail="Statistics not found for this user")
    return statistics

@app.post("/register", response_model=User)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    print("Register User:", user)
    try:
        return await create_user(db, user)
    except Exception as e:
        print("Register User:", e)
        raise HTTPException(status_code=400, detail="Error registering user") from e

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=70)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

