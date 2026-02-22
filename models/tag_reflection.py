from sqlalchemy import Column, Integer, ForeignKey
from config import Base
from sqlalchemy.orm import relationship

class TagReflection(Base):
    __tablename__ = "tag_reflection"
    __table_args__ = {'schema': 'ene'}
    
    id = Column(Integer, primary_key=True, index=True)
    reflection_id = Column(Integer, ForeignKey("ene.reflection.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("ene.tag.id"), nullable=False)
    reflection = relationship("Reflection", back_populates="tag_reflections")
    tag = relationship("Tag", back_populates="tag_reflections")