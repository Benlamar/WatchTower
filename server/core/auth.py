from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import jwt
from datetime import datetime, timezone, timedelta

from core.settings import setting
from core.security import verifyPassword
from schemas.token import TokenData, CreateToken
from schemas.user import UserInDB
from sqlalchemy.orm import Session
from crud.user import queryUserByID
from crud.token import queryCreateToken, queryToken, queryDeleteToken

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# In-memory storage for refresh tokens and blacklisted access tokens
refresh_tokens = {}
blacklisted_tokens = set()

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid Credentials",
    headers={"WWW-Authenticate": "Bearer"}
)


token_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid Token",
    headers={"WWW-Authenticate": "Bearer"}
)


def authenticateUser(username:str, password:str, db:Session):
    _user = queryUserByID(username, db)
    if _user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credentials do not exist",
        )
    try:
        pass_check = verifyPassword(password, _user.hash_password)
        if not pass_check:
            raise credentials_exception
    except Exception as e:
        print("Error authenticateuser: ",e)
        return None
    return UserInDB(id=_user.id, name=_user.name, email=_user.email, accessed=_user._accessed)


def generateAccessToken(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc)+expires_delta
    else:
        expire = datetime.now(timezone.utc)+timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encode_jwt = jwt.encode(to_encode, setting.SECRET_ACCESS_KEY, algorithm=setting.ALGORITHM)
    return encode_jwt


def generateRefreshToken(data: dict, expires_delta: Optional[timedelta] = None, user_id : int = 0, db:Session = None):
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc)+expires_delta
        else:
            expire = datetime.now(timezone.utc)+timedelta(days=setting.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_token = jwt.encode(to_encode, setting.SECRET_REFRESH_KEY, algorithm=setting.ALGORITHM)

        # insert token
        token_insert = queryCreateToken(CreateToken(token=encoded_token, user_id=user_id, expiry_date=expire, is_revoked=False), db=db)
        if not token_insert:
            return None
        return encoded_token
    except Exception as e:
        print("Error in generateRefreshToken : ", e)
        return None
 

def getRefreshToken(refresh_token: str = Cookie(None)):
    if refresh_token is None or refresh_token == "":
        return token_exception
    return refresh_token


def verifyRefreshToken(db:Session, token: str):
    # Token to check token on the database as well 
    try:
        if token is None or token == "":
            raise token_exception
        
        token_fromdb = queryToken(token, db)
        if token_fromdb is None:
            raise token_exception

        payload = jwt.decode(token, setting.SECRET_REFRESH_KEY, algorithms=[setting.ALGORITHM])

        username: str = payload.get("sub")
        if username is None or username == "":
            raise token_exception
        
        return TokenData(username=username)
    except Exception as e:
        print("Error in decode Token", e)
        raise token_exception


def verifyAccessToken(token: str):
    if token is None or token == "":
        raise token_exception
    
    try:
        payload = jwt.decode(token, setting.SECRET_ACCESS_KEY, algorithms=[setting.ALGORITHM])
        username: str = payload.get("sub")

        if username is None or username == "":
            raise token_exception
        return TokenData(username=username)
    except Exception as e:
        raise token_exception


def deleteSession(db:Session, token: str):
    try:
        delete_token = queryDeleteToken(token, db)
        if delete_token is None or token == "":
            raise token_exception
        return True
    except Exception as ex:
        print("Exception deleteSession : ",ex)
        return False
    