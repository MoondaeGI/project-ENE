from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.reflection_repository import ReflectionRepository
from repositories.message_repository import MessageRepository
from repositories.last_reflected_id_repository import LastReflectedIdRepository
from repositories.tag_reflection_repository import TagReflectionRepository
from models.reflection import Reflection
from models.message import Message
from schemas.reflection import ReflectionResponse
from utils.transactional import transactional


class ReflectionService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = ReflectionRepository(db)
        self.message_repo = MessageRepository(db)
        self.last_reflected_repo = LastReflectedIdRepository(db)
        self.tag_reflection_repo = TagReflectionRepository(db)
    
    def get_latest_reflection(self, person_id: int) -> Optional[Reflection]:
        """최신 reflection 조회 (없으면 None)"""
        return self.repo.get_latest_reflection(person_id)
    
    @transactional
    def create_reflection(self, summary: str, parent_id: Optional[int] = None) -> ReflectionResponse:
        """reflection 생성"""
        reflection = Reflection(summary=summary, parent_id=parent_id)
        created_reflection = self.repo.create(reflection)
        self.db.refresh(created_reflection)
        return ReflectionResponse.model_validate(created_reflection)
    
    @transactional
    def create_reflection_with_messages(
        self,
        summary: str,
        message_ids: List[int],
        current_message_id: int,
        person_id: int,
        tag_ids: Optional[List[int]] = None,
    ) -> ReflectionResponse:
        """
        하나의 트랜잭션으로 reflection 생성 및 모든 업데이트 처리
        (LLM 요약 생성은 트랜잭션 밖에서 수행)

        Args:
            summary: LLM으로 생성된 요약 텍스트
            message_ids: 요약에 사용된 message ID 리스트
            current_message_id: 현재 최신 message_id
            person_id: person_id
            tag_ids: reflection에 연결할 태그 id 목록 (LLM 선택/생성 결과, 최대 5개)

        Returns:
            생성된 ReflectionResponse
        """
        # 1. 이전 reflection이 있으면 parent_id로 설정
        previous_reflection = self.get_latest_reflection(person_id)
        parent_id = previous_reflection.id if previous_reflection else None

        # 2. 새 reflection 생성
        new_reflection = Reflection(summary=summary, parent_id=parent_id)
        created_reflection = self.repo.create(new_reflection)
        self.db.refresh(created_reflection)

        # 3. 사용된 message들의 reflection_id를 새 reflection.id로 업데이트
        if message_ids:
            self.message_repo.update_reflection_ids(message_ids, created_reflection.id)

        # 4. tag_reflection 연결 (최대 5개)
        if tag_ids:
            self.tag_reflection_repo.create_bulk(created_reflection.id, tag_ids)

        # 5. last_reflected_id 업데이트
        self.last_reflected_repo.create_or_update(person_id, current_message_id)

        return ReflectionResponse.model_validate(created_reflection)

