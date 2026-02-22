from typing import List, Dict, Any
from sqlalchemy.orm import Session
from repositories.tag_repository import TagRepository
from services.llm_service import llm_service


class TagService:

    def __init__(self, db: Session):
        self.db = db
        self.tag_repo = TagRepository(db)

    def get_all_for_llm(self) -> List[Dict[str, Any]]:
        """LLM에 넘길 기존 태그 목록 (id, tag)"""
        tags = self.tag_repo.get_all()
        return [{"id": t.id, "tag": t.tag} for t in tags]

    def ensure_tags(self, new_names: List[str]) -> List[int]:
        """이름으로 태그가 없으면 생성하고, 모든 태그 id 목록 반환 (중복 이름은 한 번만)"""
        if not new_names:
            return []
        seen = set()
        ids = []
        for name in (n.strip() for n in new_names if n and n.strip()):
            if name in seen:
                continue
            seen.add(name)
            existing = self.tag_repo.get_by_tag_name(name)
            if existing:
                ids.append(existing.id)
            else:
                new_tag = self.tag_repo.create_by_name(name)
                self.db.flush()
                self.db.refresh(new_tag)
                ids.append(new_tag.id)
        return ids

    async def get_tag_ids_for_content(self, content: str, max_tags: int = 5) -> List[int]:
        """
        기존 태그 전체 조회 후 LLM으로 최대 5개 선택 또는 신규 생성하고,
        선택된 id + 새로 만든 태그 id 목록 반환.
        """
        existing = self.get_all_for_llm()
        result = await llm_service.select_or_create_tags(
            existing_tags=existing,
            content=content,
            max_tags=max_tags,
        )
        selected_ids = result.get("selected_ids") or []
        new_names = result.get("new_names") or []
        new_ids = self.ensure_tags(new_names)
        return selected_ids + new_ids
