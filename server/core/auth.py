from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import jwt
from datetime import datetime, timezone, timedelta
# from uuid import uuid4

from core.settings import setting
from core.security import verifyPassword
from schemas.token import TokenData
from schemas.user import UserInDB
from sqlalchemy.orm import Session
from crud.user import queryUserByID

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# In-memory storage for refresh tokens and blacklisted access tokens
refresh_tokens = {}
blacklisted_tokens = set()

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token",
    # headers={"WWW-Authenticate": "Bearer"}
)

def authenticateUser(username:str, password:str, db:Session):
    _user = queryUserByID(username, db)
    if _user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credentials do not exist",
        )
    print("the user got is", _user)
    try:
        pass_check = verifyPassword(password, _user.hash_password)
        if not pass_check:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
    except:
        return None
    return UserInDB(**_user)


def generateAccessToken(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc)+expires_delta
    else:
        expire = datetime.now(timezone.utc)+timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encode_jwt = jwt.encode(to_encode, setting.SECRET_ACCESS_KEY, algorithm=setting.ALGORITHM)
    return encode_jwt

def generateRefreshToken(data: dict, expires_delta: Optional[timedelta] = None ):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc)+expires_delta
    else:
        expire = datetime.now(timezone.utc)+timedelta(minutes=setting.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_token = jwt.encode(to_encode, setting.SECRET_REFRESH_KEY, algorithm=setting.ALGORITHM)
    return encoded_token


def decodeToken(token: str):
    print("Decode token: ", token)
    try:
        payload = jwt.decode(token, setting.SECRET_REFRESH_KEY, algorithms=[setting.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        return token_data
    except:
        raise credentials_exception