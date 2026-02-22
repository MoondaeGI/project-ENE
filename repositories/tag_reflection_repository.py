from typing import List
from sqlalchemy.orm import Session
from models.tag_reflection import TagReflection
from repositories.base import BaseRepository


class TagReflectionRepository(BaseRepository[TagReflection]):

    def __init__(self, db: Session):
        super().__init__(TagReflection, db)

    def create(self, tag_reflection: TagReflection) -> TagReflection:
        return super().create(tag_reflection)

    def create_bulk(self, reflection_id: int, tag_ids: List[int]) -> List[TagReflection]:
        """한 reflection에 여러 태그 연결"""
        if not tag_ids:
            return []
        created = []
        for tag_id in tag_ids:
            tr = TagReflection(reflection_id=reflection_id, tag_id=tag_id)
            created.append(self.create(tr))
        return created
