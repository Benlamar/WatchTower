from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class TokenData(BaseModel):
    username: str | None = None

class RefreshToken(BaseModel):
    token: str
    expires: str