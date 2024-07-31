from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from db.database import getDB
from sqlalchemy.orm import Session
from crud.user import queryAllUsers, queryCreateUser
from schemas.user import CreateUser, DeleteUser


def getAllUsers(db: Session):
    try:
        users = queryAllUsers(db)
        return users
    except Exception as ex:
        raise HTTPException(status_code=500, detail="Failed to query all users"+ex)

def createUser(user_data: CreateUser, db: Session):
    try:
        create_user = queryCreateUser(user_data, db)
        if create_user is None:
            return None
        return create_user
    except Exception as ex:
        raise HTTPException(status_code=500, detail="Failed to query create user"+ex)
    

def removeUser(user_id: DeleteUser, db:Session):
    pass


def updateUser(db:Session):
    pass
