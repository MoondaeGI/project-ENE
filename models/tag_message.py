from sqlalchemy import Column, Integer, ForeignKey
from config import Base
from sqlalchemy.orm import relationship

class TagMessage(Base):
    __tablename__ = "tag_message"
    __table_args__ = {'schema': 'ene'}

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("ene.message.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("ene.tag.id"), nullable=False)
    message = relationship("Message", back_populates="tag_messages")
    tag = relationship("Tag", back_populates="tag_messages")