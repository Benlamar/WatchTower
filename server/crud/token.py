from sqlalchemy.orm import Session
from db.models.token import Token
from schemas.token import CreateToken


def queryCreateToken(data:CreateToken, db:Session):
    try:
        token = Token(token = data.token, 
                      user_id = data.user_id, 
                      expiry_date = data.expiry_date,
                      is_revoked = data.is_revoked
                      )
        db.add(token)
        db.commit()
        db.refresh(token)
        return token
    except:
        print("Cannot create token in the database")
        db.rollback()
        return None
    
def queryToken(token:str, db:Session):
    # try:
    #     return db.query(Token).filter(Token.token=token).one_or_none()
    # except:
    #     print("cannot find the token")
    #     return None
    pass
