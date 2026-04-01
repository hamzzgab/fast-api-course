from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Column, TIMESTAMP, text, Relationship


class Users(SQLModel, table=True):
    id: int | None = Field(index=True, primary_key=True, default=None)
    email: str = Field(unique=True)
    password: str
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    )
    posts: list["Posts"] = Relationship(back_populates="user")


class Posts(SQLModel, table=True):
    id: int | None = Field(index=True, primary_key=True, default=None)
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
    title: str
    content: str
    is_published: bool = Field(default=True)
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
        )
    )
    user: Users | None = Relationship(back_populates="posts")


class UserResponse(SQLModel):
    id: int
    email: EmailStr
    created_at: datetime


class UserCreate(SQLModel):
    email: EmailStr
    password: str


class UserLogin(SQLModel):
    email: EmailStr
    password: str


class PostUpdate(SQLModel):
    title: str
    content: str
    is_published: bool = True


class PostResponse(PostUpdate):
    id: int
    user_id: int
    user: UserResponse
    created_at: datetime


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    id: int | None
