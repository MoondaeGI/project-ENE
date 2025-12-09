from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from config import Base

class Episode(Base):
    __tablename__ = "episode"
    __table_args__ = {'schema': 'ene'}
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    importance = Column(Integer, nullable=False)
    message_id = Column(Integer, ForeignKey("ene.message.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)