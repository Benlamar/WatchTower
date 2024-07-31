from pydantic import BaseModel
from datetime import datetime

class CreateToken(BaseModel):
    token : str
    user_id : int
    expiry_date : datetime | str
    is_revoked : bool

class TokenInDB(CreateToken):
    pass

class Token(BaseModel):
    access_token: str
    refresh_token: str

class TokenData(BaseModel):
    username: str | None = None

class RefreshTokenSchema(BaseModel):
    refresh_token: str
