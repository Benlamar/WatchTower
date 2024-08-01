from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from schemas.token import Token, RefreshTokenSchema
from core.auth import authenticateUser, generateAccessToken, generateRefreshToken, oauth2_scheme, decodeToken
from core.settings import setting
from db.database import getDB

router = APIRouter()

@router.post("/login")
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
        
        content = Token(access_token=access_token).model_dump()
        response = JSONResponse(content=content, media_type="applicaiton/json")
        response.set_cookie(
            key="refresh_token",
            value=refresh_token
        )
        return response
    except Exception as e:
        print("Exception in login : ",e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error Login",
        )


@router.post("/refresh", response_model=Token)
def refreshToken(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    print("Receive are ===>", refresh_token)
    try:
        decode_data = decodeToken(refresh_token)
        access_token = generateAccessToken(data={"sub": decode_data.username, "room_id":setting.ROOM_ID})

        return Token(access_token=access_token)
    except Exception as e:
        print("Exception occured: ",e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
        )

    # refresh_token = generateRefreshToken(data={"sub": token_data.username})
    # return Token(access_token=access_token, refresh_token=refresh_token)


