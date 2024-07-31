from sqlalchemy.orm import Session
from db.models.users import Users
from schemas.user import CreateUser
from core.security import getPasswordHash

def queryAllUsers(db: Session):
    try:
        return db.query(Users).all()
    except Exception as e:
        print("Error encountered when tyrying to getAllUsers in curd :", e)
        return []
    
def queryUserByID(userid:str, db:Session):
    try:
        return db.query(Users).where(Users.name=userid).one_or_none()
        # return db.query(Users).filter(Users.name=userid).one_or_none()
    except:
        db.rollback()
        return None
    
def queryCreateUser(data: CreateUser, db: Session):
    try:
        hashed_password = getPasswordHash(data.password)
        user = Users(name=data.name, email=data.email, hash_password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        # print("Inserted user is", user)
        return user
    except:
        db.rollback()
        print("Error encountered when trying to insert camera")
        return None
