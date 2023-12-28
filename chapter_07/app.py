from fastapi import FastAPI, status, HTTPException, Depends
from chapter_07.authentication.password import get_password_hash
from sqlalchemy import exc
from chapter_07.models import User
from . import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_async_session

app = FastAPI()


@app.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=schemas.UserRead
)
async def register(
    user_create: schemas.UserCreate, session: AsyncSession = Depends(get_async_session)
) -> User:
    hashed_password = get_password_hash(user_create.password)
    user = User(
        **user_create.model_dump(exclude={"password"}), hashed_password=hashed_password
    )
    try:
        session.add(user)
        await session.commit()
    except exc.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
        )
    return user
