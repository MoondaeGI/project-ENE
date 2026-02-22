from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config import Base


class Reflection(Base):
    __tablename__ = "reflection"
    __table_args__ = {'schema': 'ene'}

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("ene.reflection.id"), nullable=True)
    summary = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    tag_reflections = relationship("TagReflection", back_populates="reflection")
