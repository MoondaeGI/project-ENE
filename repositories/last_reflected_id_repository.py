from typing import Optional
from sqlalchemy.orm import Session
from models.last_reflected_id import LastReflectedId
from repositories.base import BaseRepository


class LastReflectedIdRepository(BaseRepository[LastReflectedId]):
    
    def __init__(self, db: Session):
        super().__init__(LastReflectedId, db)
    
    def get_by_person_id(self, person_id: int) -> Optional[LastReflectedId]:
        """person_id로 조회"""
        return self.db.query(LastReflectedId).filter(LastReflectedId.id == person_id).first()
    
    def create_or_update(self, person_id: int, message_id: int) -> LastReflectedId:
        """생성 또는 업데이트"""
        existing = self.get_by_person_id(person_id)
        if existing:
            existing.message_id = message_id
            self.db.flush()
            return existing
        else:
            new_record = LastReflectedId(id=person_id, message_id=message_id)
            return self.create(new_record)

