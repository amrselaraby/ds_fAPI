from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from tortoise.models import Model
from tortoise import fields


class PostBase(BaseModel):
    title: str
    content: str
    publication_date: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class PostPartialUpdate(BaseModel):
    content: Optional[str] = None
    title: Optional[str] = None


class PostCreate(PostBase):
    pass


class PostDB(PostBase):
    id: int


class PostTortoise(Model):
    id = fields.IntField(pk=True, generated=True)
    publication_date = fields.DatetimeField(null=False)
    title = fields.CharField(max_length=255, null=False)
    content = fields.TextField(null=False)

    class Meta:
        table = "posts"
