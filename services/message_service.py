from typing import List, Optional
from sqlalchemy.orm import Session
from repositories import MessageRepository
from models.message import Message
from schemas.message import MessageCreate, MessageResponse
from utils.transactional import transactional


class MessageService:
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = MessageRepository(db)
    
    @transactional
    def create_message(self, message_data: MessageCreate) -> MessageResponse:
        message = Message(person_id=message_data.person_id, content=message_data.content)
        created_message = self.repo.create(message)
        self.db.refresh(created_message) 

        return MessageResponse.model_validate(created_message)
    
    def get_message(self, message_id: int) -> Optional[MessageResponse]:
        message = self.repo.get(message_id)
        
        if not message:
            return None
        return MessageResponse.model_validate(message)
    