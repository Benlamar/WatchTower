from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, 
from typing import Annotated
from schemas.token import Token
from core.auth import authenticateUser, generateAccessToken, generateRefreshToken, oauth2_scheme, decodeToken
from core.settings import setting

router = APIRouter()

@router.post("/login", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db:Session = Depends(getDB)):
    auth = authenticateUser(form_data.username, form_data.password, db)
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = generateAccessToken(data={"sub": auth.name, "room_id":setting.ROOM_ID})
    refresh_token = generateRefreshToken(data={"sub":auth.name})
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
def refreshToken(token: str = Depends(oauth2_scheme)):
    token_data = decodeToken(token)
    access_token = generateAccessToken(data={"sub": token_data.username, "room_id":setting.ROOM_ID})
    refresh_token = generateRefreshToken(data={"sub": token_data.username})
    return Token(access_token=access_token, refresh_token=refresh_token)


