from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=6, max_length=100)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=6, max_length=100)


class ProjectJoin(BaseModel):
    invite_code: str = Field(min_length=6, max_length=64)
    password: str = Field(min_length=1, max_length=100)


class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class ProjectOut(BaseModel):
    id: int
    name: str
    owner_id: int
    invite_code: str
    member_count: int = 0
    is_owner: bool = False

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    content: str = Field(min_length=1, max_length=500)


class TaskOut(BaseModel):
    id: int
    project_id: int
    username: str
    content: str
    likes: int
    dislikes: int
    status: Optional[str]
    statusby: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class CommentOut(BaseModel):
    id: int
    task_id: int
    username: str
    content: str
    likes: int
    dislikes: int
    created_at: datetime

    class Config:
        from_attributes = True
