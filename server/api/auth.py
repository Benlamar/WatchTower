from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from schemas.token import Token, TokenData
from core.auth import (authenticateUser, generateAccessToken, 
                       generateRefreshToken, verifyRefreshToken, getRefreshToken,
                       deleteSession)
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
            headers={"WWW-Authenticate": "Bearer"}
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
            value=refresh_token,
            httponly=True,
            secure=True,
            expires=setting.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
        )
        return response
    except Exception as e:
        print("Exception in login : ",e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error Login",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/refresh")
def refreshToken(db: Session = Depends(getDB), token:str = Depends(getRefreshToken)):
    try:
        #TODO more on verifytoken
        token_data = verifyRefreshToken(db, token)
        access_token = generateAccessToken(data={"sub": token_data.username, "room_id":setting.ROOM_ID})
        return Token(access_token=access_token)
    except Exception as e:
        print("Error refreshToken: ",e)
        # return Response(status_code=400).delete_cookie("refresh_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/logout")
def logout(db:Session = Depends(getDB), token:str = Depends(getRefreshToken)):
    try:
        delete_session:bool = deleteSession(db, token)
        if not delete_session:
            raise Exception("Can not delete session from db")
        response = JSONResponse(status_code=200, content={"msg":"Successfull"})
    except Exception as ex:
        print("Exception ",ex)
        response = JSONResponse(status_code=400, content={"msg":"Token missing"})
    finally:
        response.delete_cookie("refresh_token")
    return response