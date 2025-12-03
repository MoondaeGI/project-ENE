from typing import Optional, List
from sqlalchemy.orm import Session
from models.person import Person
from repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    
    def __init__(self, db: Session):
        super().__init__(Message, db)
    
    
    def get_all(self) -> List[Message]:
        return self.db.query(Message).all()

    
    def create(self, message: Message) -> Message:
        return super().create(message)

