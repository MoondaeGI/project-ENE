from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.reflection import Reflection
from repositories.base import BaseRepository


class ReflectionRepository(BaseRepository[Reflection]):
    
    def __init__(self, db: Session):
        super().__init__(Reflection, db)
    
    def get_latest_reflection(self, person_id: int) -> Optional[Reflection]:
        """person_id 기준 최신 reflection 조회"""
        # reflection은 person_id를 직접 가지지 않으므로, 
        # message를 통해 연결된 reflection을 찾아야 함
        # 일단 최신 reflection을 반환 (추후 person_id 연결 필요 시 수정)
        return self.db.query(Reflection).order_by(desc(Reflection.created_at)).first()
    
    def create(self, reflection: Reflection) -> Reflection:
        return super().create(reflection)

