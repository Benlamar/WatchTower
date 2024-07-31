from pydantic import BaseModel

class CreateToken(BaseModel):
    token : str
    user_id : int
    expiry_date : str
    is_revoked : str

class TokenInDB(CreateToken):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class TokenData(BaseModel):
    username: str | None = None

class RefreshToken(BaseModel):
    token: str
    expires: str