from sqlalchemy.orm import Session
from db.models.token import Tokens
from schemas.token import CreateToken


def queryCreateToken(data:CreateToken, db:Session):
    try:
        token = Tokens(token = data.token, 
                      user_id = data.user_id, 
                      expiry_date = data.expiry_date,
                      is_revoked = data.is_revoked
                      )
        db.add(token)
        db.commit()
        db.refresh(token)
        return token
    except Exception as e:
        print("Cannot create token in the database {e}")
        db.rollback()
        return None

def queryTokenByUserID(user_id:int, db: Session):
    try:
        existing_token = db.query(Tokens).filter(Tokens.user_id.is_(user_id)).one()
        if not existing_token:
            return None
        return existing_token     
    except Exception as e:
        print("Error in querying token {e}")
        return None
    
def queryToken(token:str, db:Session):
    try:
        return db.query(Tokens).filter(Tokens.token.is_(token)).one()
    except:
        print("cannot find the token in db")
        return None


def queryDeleteToken(token:str, db:Session):
    try:
        token = db.query(Tokens).filter(Tokens.token.is_(token)).one()
        if token:
            db.delete(token)
            db.commit()
            return True
        return False
    except Exception as ex:
        db.rollback()
        print("Expection queryDeleteToken : ", ex)
        return False