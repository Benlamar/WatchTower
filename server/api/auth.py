from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from schemas.token import Token, RefreshTokenSchema
from core.auth import authenticateUser, generateAccessToken, generateRefreshToken, oauth2_scheme, decodeToken
from core.settings import setting
from db.database import getDB

router = APIRouter()

@router.post("/login", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db:Session = Depends(getDB)):
    auth = authenticateUser(form_data.username, form_data.password, db)
    print("Authenticate ", auth)
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    try:
        access_token = generateAccessToken(data={"sub": auth.name, "room_id":setting.ROOM_ID})
        refresh_token = generateRefreshToken(data={"sub":auth.name}, user_id=auth.id, db=db)
        if (access_token is None or refresh_token is None):
            raise Exception("Tokens could not be generated")
        print("Tokens are ", access_token, "===>", refresh_token)
    
        return Token(access_token=access_token, refresh_token=refresh_token)
    except Exception as e:
        print("Exception in login : ",e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error",
        )


@router.post("/refresh", response_model=Token)
def refreshToken(token: RefreshTokenSchema):
    print("Receive are ===>", token.refresh_token)
    token_data = decodeToken(token.refresh_token)
    access_token = generateAccessToken(data={"sub": token_data.username, "room_id":setting.ROOM_ID})
    refresh_token = generateRefreshToken(data={"sub": token_data.username})
    return Token(access_token=access_token, refresh_token=refresh_token)


