from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from config import Base

class Reflection(Base):
    __tablename__ = "reflection"
    
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("reflection.id"), nullable=True)
    summary = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
