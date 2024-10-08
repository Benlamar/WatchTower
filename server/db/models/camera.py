from db.database import Base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone

class Camera(Base):
    __tablename__ = "camera"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cam_name = Column(String(100), index=True)
    location = Column(String(100)) # unique=True
    source = Column(String(255), unique=True)
    boundary = Column(String(255), nullable=True)
    task = Column(String(255), nullable=True)
    
    _created = Column(DateTime(), default=datetime.now(timezone.utc))
    _accessed = Column(DateTime(), 
                       default=datetime.now(timezone.utc),
                       onupdate=datetime.now(timezone.utc))