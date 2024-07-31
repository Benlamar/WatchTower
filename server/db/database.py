from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from core.settings import setting

engine = create_engine(setting.DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False,
                            autocommit=False,
                            bind=engine)
Base = declarative_base()

def startDB():
    Base.metadata.create_all(bind=engine)
    
def getDB():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        