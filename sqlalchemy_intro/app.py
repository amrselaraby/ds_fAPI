import contextlib
from fastapi import Depends, FastAPI, Query, status, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from .database import create_all_tables, get_async_session
from typing import Sequence, Tuple

from .models import Comment, Post
from .schemas import PostPartialUpdate, PostRead, PostCreate
from . import schemas


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    await create_all_tables()
    yield


class Pagination:
    def __init__(self, maximum_limit: int = 100) -> None:
        self.maximum_limit = maximum_limit

    async def __call__(
        self, skip: int = Query(0, ge=0), limit: int = Query(10, ge=0)
    ) -> Tuple[int, int]:
        capped_limit = min(self.maximum_limit, limit)
        return (skip, capped_limit)


async def get_post_or_404(
    id: int, session: AsyncSession = Depends(get_async_session)
) -> Post:
    select_query = (
        select(Post).options(selectinload(Post.comments)).where(Post.id == id)
    )
    result = await session.execute(select_query)
    post = result.scalar_one_or_none()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return post


app = FastAPI(lifespan=lifespan)
pagination = Pagination(maximum_limit=50)


@app.get("/posts", response_model=list[PostRead])
async def list_posts(
    pagination: tuple[int, int] = Depends(pagination),
    session: AsyncSession = Depends(get_async_session),
) -> Sequence[Post]:
    skip, limit = pagination
    select_query = select(Post).offset(skip).limit(limit)
    result = await session.execute(select_query)
    return result.scalars().all()


@app.post("/posts", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_create: PostCreate, session: AsyncSession = Depends(get_async_session)
) -> Post:
    post = Post(**post_create.model_dump())
    session.add(post)
    await session.commit()

    return post


@app.get("/posts/{id}", response_model=PostRead)
async def get_post(post: Post = Depends(get_post_or_404)) -> Post:
    return post


@app.patch("/posts/{id}", response_model=PostRead)
async def update_post(
    post_update: PostPartialUpdate,
    post: Post = Depends(get_post_or_404),
    session: AsyncSession = Depends(get_async_session),
) -> Post:
    post_update_dict = post_update.model_dump(exclude_unset=True)
    for key, value in post_update_dict.items():
        setattr(post, key, value)
    session.add(post)
    await session.commit()
    return post


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post: Post = Depends(get_post_or_404),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    await session.delete(post)
    await session.commit()


# ======================= Comments =================================
@app.post(
    "/posts/{id}/comments",
    response_model=schemas.CommentRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    comment_create: schemas.CommentCreate,
    post: Post = Depends(get_post_or_404),
    session: AsyncSession = Depends(get_async_session),
) -> Comment:
    comment = Comment(**comment_create.model_dump(), post=post)
    session.add(comment)
    await session.commit()
    return comment
