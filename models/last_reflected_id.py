from sqlalchemy import Column, Integer, ForeignKey
from config import Base


class LastReflectedId(Base):
    __tablename__ = "last_reflected_id"
    __table_args__ = {'schema': 'ene'}
    
    id = Column(Integer, ForeignKey("ene.person.id"), primary_key=True, nullable=False)
    message_id = Column(Integer, ForeignKey("ene.message.id"), nullable=True)