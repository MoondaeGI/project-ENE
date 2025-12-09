from typing import List
from sqlalchemy.orm import Session
from models.message import Message
from repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    
    def __init__(self, db: Session):
        super().__init__(Message, db)
    

    def get_all(self) -> List[Message]:
        return self.db.query(Message).all()

    
    def create(self, message: Message) -> Message:
        return super().create(message)
    
    def get_messages_after(self, message_id: int) -> List[Message]:
        start_id = 1 if message_id == 0 else message_id + 1
        return (
            self.db.query(Message)
            .filter(Message.id >= start_id)
            .order_by(Message.id)
            .all()
        )
    
    def update_reflection_ids(self, message_ids: List[int], reflection_id: int) -> int:
        updated_count = self.db.query(Message).filter(
            Message.id.in_(message_ids)
        ).update(
            {Message.reflection_id: reflection_id},
            synchronize_session=False
        )
        self.db.flush()
        return updated_count

