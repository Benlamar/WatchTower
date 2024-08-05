from db.database import Base
from sqlalchemy import Column, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class Tokens(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    token = Column(Text, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    expiry_date = Column(DateTime(timezone=True))
    is_revoked = Column(Boolean, default=False)

    _created = Column(DateTime(), default=datetime.now(timezone.utc))
    _accessed = Column(DateTime(), 
                       default=datetime.now(timezone.utc),
                       onupdate=datetime.now(timezone.utc))
    
    user = relationship("Users", 
                        back_populates="token")