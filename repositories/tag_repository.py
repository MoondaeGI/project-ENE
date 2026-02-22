from typing import List, Optional
from sqlalchemy.orm import Session
from models.tag import Tag
from repositories.base import BaseRepository


class TagRepository(BaseRepository[Tag]):

    def __init__(self, db: Session):
        super().__init__(Tag, db)

    def get_all(self, skip: int = 0, limit: int = 1000) -> List[Tag]:
        return self.db.query(Tag).order_by(Tag.id).offset(skip).limit(limit).all()

    def get_by_tag_name(self, tag_name: str) -> Optional[Tag]:
        return self.db.query(Tag).filter(Tag.tag == tag_name).first()

    def create(self, tag: Tag) -> Tag:
        return super().create(tag)

    def create_by_name(self, tag_name: str) -> Tag:
        tag = Tag(tag=tag_name)
        return self.create(tag)
