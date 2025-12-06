from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from config import Base

class Message(Base):
    __tablename__ = "message"
    
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("person.id"), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
