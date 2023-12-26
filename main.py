from fastapi import Depends, FastAPI, Query, status, HTTPException
from pydantic import BaseModel
from typing import Tuple

from models import PostCreate, PostDB, PostTortoise


class Post(BaseModel):
    title: str


class PublicPost(BaseModel):
    title: str


class Pagination:
    def __init__(self, maximum_limit: int = 100) -> None:
        self.maximum_limit = maximum_limit

    async def __call__(
        self, skip: int = Query(0, ge=0), limit: int = Query(10, ge=0)
    ) -> Tuple[int, int]:
        capped_limit = min(self.maximum_limit, limit)
        return (skip, capped_limit)


# Dummy Database
posts = {1: Post(title="Hello")}

app = FastAPI()

pagination = Pagination(maximum_limit=50)


async def get_post_or_404(id: int) -> Post:
    try:
        return posts[id]
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.get("/posts/{id}")
async def get(post: Post = Depends(get_post_or_404)):
    return post


@app.get("/items")
async def list_items(p: Tuple[int, int] = Depends(pagination)):
    skip, limit = p
    return {"skip": skip, "limit": limit}


@app.post("/posts", response_model=PostDB, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate) -> PostDB:
    post_tortoise = await PostTortoise.create(**post.dict())

    return PostDB.from_attributes(post_tortoise)
