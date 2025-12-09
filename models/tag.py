from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from config import Base

class Tag(Base):
    __tablename__ = "tag"
    __table_args__ = {'schema': 'ene'}
    
    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)