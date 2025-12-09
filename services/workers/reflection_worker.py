import asyncio
import logging
import threading
from typing import List, Optional, Tuple

from config.database_config import SessionLocal
from services.llm_service import llm_service
from services.reflection_service import ReflectionService

logger = logging.getLogger(__name__)


class ReflectionWorker:

    def start(
        self,
        person_id: int,
        current_message_id: int,
        messages: List[Tuple[int, str]],
        reflection_summary: Optional[str],
    ) -> None:
        thread = threading.Thread(
            target=self._run_worker,
            args=(person_id, current_message_id, messages, reflection_summary),
            daemon=True,
        )
        thread.start()

    def _run_worker(
        self,
        person_id: int,
        current_message_id: int,
        messages: List[Tuple[int, str]],
        reflection_summary: Optional[str],
    ) -> None:
        db = SessionLocal()
        try:
            reflection_service = ReflectionService(db)
            message_ids = [msg_id for msg_id, _ in messages]
            message_contents = [content for _, content in messages]

            summary = asyncio.run(self._generate_summary(reflection_summary, message_contents))

            reflection_service.create_reflection_with_messages(
                summary=summary,
                message_ids=message_ids,
                current_message_id=current_message_id,
                person_id=person_id,
            )
            logger.info("[ReflectionWorker] Reflection 생성 완료 - message_id: %s", current_message_id)
        except Exception as e:
            error_msg = str(e).encode("utf-8", errors="replace").decode("utf-8")
            logger.error("[ReflectionWorker] Reflection 처리 실패: %s", error_msg)
            logger.exception(e)
        finally:
            db.close()

    async def _generate_summary(
        self, reflection_summary: Optional[str], message_contents: List[str]
    ) -> str:
        return await llm_service.generate_summary(reflection_summary, message_contents)


reflection_worker = ReflectionWorker()
