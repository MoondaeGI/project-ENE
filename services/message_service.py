from typing import List, Optional
from sqlalchemy.orm import Session
from repositories import MessageRepository, TagMessageRepository
from services.tag_service import TagService
from models.message import Message, MessageAction
from schemas.message import PersonMessageCreate, AIMessageCreate, MessageResponse
from utils.transactional import transactional


class MessageService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = MessageRepository(db)
        self.tag_message_repo = TagMessageRepository(db)
        self.tag_service = TagService(db)
    
    @transactional
    def create_person_message(self, message_data: PersonMessageCreate) -> MessageResponse:
        """사용자 메시지 생성"""
        message = Message(
            person_id=message_data.person_id,
            content=message_data.content,
            action=MessageAction.PERSON
        )
        created_message = self.repo.create(message)
        self.db.refresh(created_message)

        return MessageResponse.model_validate(created_message)

    async def attach_tags_for_content(self, message_id: int, content: str) -> None:
        """메시지 내용 기준으로 LLM이 태그 선택/생성 후 tag_message에 연결 (최대 5개)"""
        tag_ids = await self.tag_service.get_tag_ids_for_content(content, max_tags=5)
        if tag_ids:
            self.tag_message_repo.create_bulk(message_id, tag_ids)

    @transactional
    def create_ai_message(self, message_data: AIMessageCreate) -> MessageResponse:
        """AI 메시지 생성"""
        message = Message(
            person_id=None,
            content=message_data.content,
            action=MessageAction.AI
        )
        created_message = self.repo.create(message)
        self.db.refresh(created_message)

        return MessageResponse.model_validate(created_message)

    def get_message(self, message_id: int) -> Optional[MessageResponse]:
        message = self.repo.get(message_id)
        
        if not message:
            return None
        return MessageResponse.model_validate(message)
    
    def get_messages_after(self, message_id: int) -> List[Message]:
        return self.repo.get_messages_after(message_id)
    