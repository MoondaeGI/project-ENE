from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from config import Base


class MessageAction(enum.Enum):
    AI = "AI"
    PERSON = "PERSON"


class Message(Base):
    __tablename__ = "message"
    __table_args__ = {'schema': 'ene'}

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("ene.person.id"), nullable=True)
    content = Column(String, nullable=False)
    action = Column(Enum(MessageAction), nullable=False, default=MessageAction.PERSON)
    reflection_id = Column(Integer, ForeignKey("ene.reflection.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    tag_messages = relationship("TagMessage", back_populates="message")
