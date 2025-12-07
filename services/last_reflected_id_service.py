from typing import Optional
from sqlalchemy.orm import Session
from repositories.last_reflected_id_repository import LastReflectedIdRepository
from utils.transactional import transactional


class LastReflectedIdService:
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = LastReflectedIdRepository(db)
    
    def get_last_reflected_message_id(self, person_id: int) -> int:
        """마지막 reflection된 message_id 조회 (없으면 0)"""
        last_reflected = self.repo.get_by_person_id(person_id)
        if not last_reflected or not last_reflected.message_id:
            return 0
        return last_reflected.message_id
    
    @transactional
    def update_last_reflected_id(self, person_id: int, message_id: int):
        """last_reflected_id 업데이트"""
        self.repo.create_or_update(person_id, message_id)

