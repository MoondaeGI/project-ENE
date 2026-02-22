import asyncio
import logging
import threading
from typing import List, Optional, Tuple

from config.database_config import SessionLocal
from services.llm_service import llm_service
from services.reflection_service import ReflectionService
from services.tag_service import TagService

logger = logging.getLogger(__name__)


class ReflectionWorker:

    def start(
        self,
        person_id: int,
        current_message_id: int,
        messages_with_roles: List[Tuple[int, str, str]],
        reflection_summary: Optional[str],
    ) -> None:
        thread = threading.Thread(
            target=self._run_worker,
            args=(person_id, current_message_id, messages_with_roles, reflection_summary),
            daemon=True,
        )
        thread.start()

    def _run_worker(
        self,
        person_id: int,
        current_message_id: int,
        messages_with_roles: List[Tuple[int, str, str]],
        reflection_summary: Optional[str],
    ) -> None:
        db = SessionLocal()
        try:
            reflection_service = ReflectionService(db)
            tag_service = TagService(db)
            message_ids = [msg_id for msg_id, _, _ in messages_with_roles]

            summary = asyncio.run(
                self._generate_summary(reflection_summary, messages_with_roles)
            )

            tag_ids = asyncio.run(
                tag_service.get_tag_ids_for_content(summary, max_tags=5)
            )

            reflection_service.create_reflection_with_messages(
                summary=summary,
                message_ids=message_ids,
                current_message_id=current_message_id,
                person_id=person_id,
                tag_ids=tag_ids,
            )
            logger.info("[ReflectionWorker] Reflection 생성 완료 - message_id: %s", current_message_id)
        except Exception as e:
            error_msg = str(e).encode("utf-8", errors="replace").decode("utf-8")
            logger.error("[ReflectionWorker] Reflection 처리 실패: %s", error_msg)
            logger.exception(e)
        finally:
            db.close()

    async def _generate_summary(
        self, reflection_summary: Optional[str], messages_with_roles: List[Tuple[int, str, str]]
    ) -> str:
        return await llm_service.generate_summary(
            reflection_summary,
            messages=[],
            messages_with_roles=[(role, content) for _, content, role in messages_with_roles],
        )


reflection_worker = ReflectionWorker()
