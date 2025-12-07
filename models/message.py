from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from config import Base


class MessageAction(enum.Enum):
    AI = "AI"
    PERSON = "PERSON"


class Message(Base):
    __tablename__ = "message"
    
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("person.id"), nullable=True)
    content = Column(String, nullable=False)
    action = Column(Enum(MessageAction), nullable=False, default=MessageAction.PERSON)
    reflection_id = Column(Integer, ForeignKey("reflection.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
