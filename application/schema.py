from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, Field


class User(BaseModel):
    id: Optional[int]
    username: str
    password: str
    mobile: str
    credit_card: str
    service: str
    calls_remaining: int


class ShowUser(BaseModel):
    username: str

    class Config:
        orm_mode = True


class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None
