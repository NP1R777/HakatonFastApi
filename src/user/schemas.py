import uuid
from datetime import datetime
from typing_extensions import List
from pydantic import BaseModel, Field


class UserIn:
    class Create(BaseModel):
        username: str
        password: str
        phone: str
        preferences: List[int]

    class Login(BaseModel):
        username: str
        password: str


class UserTokenPayload(BaseModel):
    jti: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int


class UserOut:

    class Base(BaseModel):
        created_at: datetime | None
        update_at: datetime | None
        deleted_at: datetime | None
        id: int

    class Create(Base):
        username: str
        phone: str
        preferences: List[int]

    class Me(Base):
        username: str
        password: str
        refresh_token: str


class UserUpdate(BaseModel):
    username: None
    password: None
    phone: None
    preferences: List[None]


class TokenResponse(BaseModel):
    user_id: int
    username: str
    access_token: str | None
    refresh_token: str | None
    token_type: str
