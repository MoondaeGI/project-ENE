from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from config import Base

class Person(Base):
    __tablename__ = "person"
    __table_args__ = {'schema': 'ene'}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

