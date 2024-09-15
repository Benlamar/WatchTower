from sqlalchemy.orm import Session
from db.models.token import Tokens
from schemas.token import CreateToken


def queryCreateToken(data: CreateToken, db: Session):
    try:
        # Check if a token already exists for the user
        existing_token = db.query(Tokens).filter(Tokens.user_id == data.user_id).first()
        
        if existing_token:
            # Update the existing token
            existing_token.token = data.token
            existing_token.expiry_date = data.expiry_date
            existing_token.is_revoked = data.is_revoked
            db.commit()
            db.refresh(existing_token)
            return existing_token
        else:
            # Create a new token if none exists
            token = Tokens(
                token=data.token,
                user_id=data.user_id,
                expiry_date=data.expiry_date,
                is_revoked=data.is_revoked
            )
            db.add(token)
            db.commit()
            db.refresh(token)
            return token
    except Exception as e:
        print(f"Cannot create or update token in the database: {e}")
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