from db.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from datetime import datetime, timezone

class Token(Base):
    __tablename__ = "token"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(Text, index=True)
    user_id = Column(Integer, index=True)
    expiry_date = Column(DateTime)
    is_revoked = Column(Boolean, default=False)

    _created = Column(DateTime(), default=datetime.now(timezone.utc))
    _accessed = Column(DateTime(), default=datetime.now(timezone.utc))