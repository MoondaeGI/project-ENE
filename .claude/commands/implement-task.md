# Implement Task

`.kiro/specs/ai-character-chat-system/tasks.md`에서 지정한 태스크를 구현합니다.

## 사용법

```
/implement-task <태스크 번호>
예: /implement-task 2.1
```

## 구현 전 체크리스트

구현 전 반드시 확인:
1. **요구사항 추적**: tasks.md의 `_Requirements:` 항목 → `requirements.md`에서 acceptance criteria 확인
2. **설계 참조**: 해당 컴포넌트의 design 파일 (`.kiro/specs/ai-character-chat-system/design/`) 확인
3. **의존성 파악**: 이전 태스크가 완료되었는지 확인

## 구현 원칙

- **Memory Object**: `importance_score`, `memory_strength`, `access_count`, `created_at`, `last_access_time` 반드시 포함
- **LLM Provider**: `LLMProvider` Protocol 구현 (기존 코드 수정 없이 플러그인 추가)
- **에이전트**: LangGraph `StateGraph`로 오케스트레이션, 독립적 동작
- **의존성 방향**: `api → workflow → services → database` (역방향 금지)
- **비동기**: 모든 DB/LLM 호출은 `async/await`

## 태스크별 참조 파일

| 태스크 | 참조 design 파일 |
|--------|----------------|
| Task 2 (LLM Adapter) | `design/05_llm_adapter.md` |
| Task 4-6 (Memory) | `design/03_memory_system.md` |
| Task 8 (Reflection) | `design/03_memory_system.md` |
| Task 9 (Episode) | `design/04_data_models.md` |
| Task 10 (Portrait) | `design/03_memory_system.md` |
| Task 12 (Emotion) | `design/02_agents.md` |
| Task 13 (Planning) | `design/02_agents.md` |
| Task 17-19 (Workflow) | `design/01_workflow.md` |
| Task 22 (WebSocket) | `design/01_workflow.md` |

## 구현 후 확인

```bash
# 단위 테스트 실행
python -m pytest tests/unit/ -v

# 통합 테스트 (해당 태스크가 통합 테스트인 경우)
python -m pytest tests/integration/ -v
```

태스크를 완료하면 `tasks.md`에서 `[ ]` → `[x]`로 업데이트하세요.

---

## 현재 구현 대상: $ARGUMENTS
