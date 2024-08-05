from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: str | None=None

class CreateUser(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    accessed: datetime

class DeleteUser(BaseModel):
    id: int
