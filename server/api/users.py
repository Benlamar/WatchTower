from fastapi import APIRouter, Depends, Form, HTTPException
from core.users import getAllUsers, createUser
from core.auth import oauth2_scheme
from schemas.user import CreateUser, UserInDB
from db.database import getDB
from sqlalchemy.orm import Session
import json

router = APIRouter()

@router.get("/")
def users(db:Session = Depends(getDB), token = Depends(oauth2_scheme)):

    print("Token ==>", token)
    res_raw = getAllUsers(db)

    if res_raw is not None:
        data = [UserInDB(id=x.id, name=x.name, email=x.email, accessed=x._accessed) for x in res_raw]   
        return data
    return []

@router.post("/create")
def create(user: CreateUser, db:Session = Depends(getDB)):
    res = createUser(user, db)
    if res is not None:
        data = UserInDB(id=res.id, name=res.name, email=res.email, accessed=res._accessed)
        return data
    else:
        raise HTTPException(detail="Failed to create user", status_code=400)