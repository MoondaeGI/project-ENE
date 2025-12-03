from typing import List, Optional
from sqlalchemy.orm import Session
from repositories import MessageRepository
from models.message import Message
from schemas.message import MessageCreate, MessageResponse


class MessageService:
    
    @staticmethod
    def create_message(message_data: MessageCreate, db: Session) -> MessageResponse:
        repo = MessageRepository(db)
        message = Message(person_id=message_data.person_id, content=message_data.content)
        created_message = repo.create(message)
        db.flush()
        db.refresh(created_message) 

        return MessageResponse.model_validate(created_message)
    
    @staticmethod
    def get_message(message_id: int, db: Session) -> Optional[MessageResponse]:
        repo = MessageRepository(db)
        message = repo.get(message_id)
        
        if not message:
            return None
        return MessageResponse.model_validate(message)
    