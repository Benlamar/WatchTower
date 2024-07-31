from db.database import Base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), index=True)
    email = Column(String(100), unique=True, index=True)
    hash_password = Column(String(255))
    
    _created = Column(DateTime(), default=datetime.now(timezone.utc))
    _accessed = Column(DateTime(), default=datetime.now(timezone.utc))