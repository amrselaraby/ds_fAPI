from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import Integer, String


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    email: Mapped[str] = mapped_column(
        String(1024), index=True, unique=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
