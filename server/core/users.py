from fastapi.exceptions import HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session
from crud.user import queryAllUsers, queryCreateUser
from schemas.user import CreateUser, DeleteUser
from core.auth import oauth2_scheme


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
            raise HTTPException(status_code=500, detail="Failed to query create user")
        return create_user
    except Exception as ex:
        print("Error createUser: ", ex)
        raise HTTPException(status_code=500, detail="Failed to query create user")
    

def removeUser(user_id: DeleteUser, db:Session):
    pass


def updateUser(db:Session):
    pass
