from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from schemas.token import Token

router = APIRouter()

@router.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return "Login Successful"


# @router.post("/refresh")
# def refreshToken(refresh_token: str):
#     return "Refresh Successfull"
