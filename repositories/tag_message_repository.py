from typing import List
from sqlalchemy.orm import Session
from models.tag_message import TagMessage
from repositories.base import BaseRepository


class TagMessageRepository(BaseRepository[TagMessage]):

    def __init__(self, db: Session):
        super().__init__(TagMessage, db)

    def create(self, tag_message: TagMessage) -> TagMessage:
        return super().create(tag_message)

    def create_bulk(self, message_id: int, tag_ids: List[int]) -> List[TagMessage]:
        """한 메시지에 여러 태그 연결"""
        if not tag_ids:
            return []
        created = []
        for tag_id in tag_ids:
            tm = TagMessage(message_id=message_id, tag_id=tag_id)
            created.append(self.create(tm))
        return created
