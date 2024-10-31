# schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from utils import TrimmedBaseModel

class UserCreate(TrimmedBaseModel):
    username: str = Field(..., max_length=30)
    password: str = Field(..., min_length=6)

class BookCreate(TrimmedBaseModel):
    title: str = Field(..., max_length=100)
    author: str = Field(..., max_length=100)
    available: bool = Field(default=True)


class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool

    class Config:
        orm_mode = True

class BookCreate(BaseModel):
    title: str
    author: str

class BookOut(BaseModel):
    id: int
    title: str
    author: str
    available: bool

    class Config:
        orm_mode = True
