# AI Character Chat System

Memory-based AI 캐릭터 채팅 시스템. 사용자와 장기적 관계를 형성하고 축적된 맥락으로 자연스러운 대화를 제공하는 **multi-agent 시스템**.

## 기술 스택

| 분류            | 기술                                       |
| --------------- | ------------------------------------------ |
| Language        | Python 3.11+                               |
| Web Framework   | FastAPI (비동기, WebSocket)                |
| Multi-Agent     | LangGraph (StateGraph 기반)                |
| LLM Integration | LangChain                                  |
| Database        | PostgreSQL + pgvector (HNSW, VECTOR(1536)) |
| Deployment      | AWS Cloud                                  |
| Context Limit   | 200,000 토큰                               |

LLM Providers (플러그인): OpenAI, Anthropic, Google Gemini / Ollama, LM Studio, LocalAI

## 아키텍처

```text
api → workflow → services → database   (단방향 의존)
               ↘ models ↗
core (모든 레이어), background → services → database
```

**메인 워크플로우**: Autonomous Behavior → Memory Retrieval → Emotion Analysis → Dialogue Planning → Message Generation → Memory Save

**Memory Stream 계층**: `Message → Observation → Episode → Reflection → User Portrait`

## 참고 문서

`.claude/docs/` 안에 있습니다.

| 문서                                                                          | 내용                                   |
| ----------------------------------------------------------------------------- | -------------------------------------- |
| [requirements.md](.claude/docs/requirements.md)                               | 전체 요구사항 및 Acceptance Criteria   |
| [tasks.md](.claude/docs/tasks.md)                                             | 구현 태스크 목록 및 현황               |
| [design/00_overview.md](.claude/docs/design/00_overview.md)                   | 시스템 개요, Retrieval Score 공식      |
| [design/01_workflow.md](.claude/docs/design/01_workflow.md)                   | LangGraph 워크플로우, Chain/Subgraph   |
| [design/02_agents.md](.claude/docs/design/02_agents.md)                       | 7개 에이전트 설계, ConversationPolicy  |
| [design/03_memory_system.md](.claude/docs/design/03_memory_system.md)         | Memory Stream, Retrieval, Evolution    |
| [design/04_data_models.md](.claude/docs/design/04_data_models.md)             | DB 스키마 초기 설계                    |
| [design/05_llm_adapter.md](.claude/docs/design/05_llm_adapter.md)             | LLMProvider Protocol, LLMAdapter       |
| [design/06_patterns.md](.claude/docs/design/06_patterns.md)                   | 핵심 코드 패턴 모음                    |
| [design/07_error_handling.md](.claude/docs/design/07_error_handling.md)       | 에러 처리 전략                         |
| [design/08_testing.md](.claude/docs/design/08_testing.md)                     | 테스트 전략 및 성능 목표               |
| [design/09_project_structure.md](.claude/docs/design/09_project_structure.md) | 전체 디렉터리 구조, 레이어별 파일 목록 |
| [design/10_database_schema.md](.claude/docs/design/10_database_schema.md)     | 전체 DDL (최신), ERD, 설계 결정 사항   |
| [design/11_aws_architecture.md](.claude/docs/design/11_aws_architecture.md)   | AWS 배포 아키텍처, 비용, 확장 포인트   |

## 코딩 가이드라인

### 구현 전 주석 확인 절차

함수를 구현하기 전에 반드시 아래 절차를 따릅니다.

1. **스텁 작성**: 함수 시그니처 + docstring 형태로 역할, 파라미터, 반환값을 먼저 작성합니다.
2. **사용자 확인**: 스텁을 보여주고 구현 방향이 맞는지 확인 요청합니다.
3. **승인 후 구현**: 확인 받은 뒤에만 실제 로직을 작성합니다.

스텁 예시:

```python
async def retrieve_memories(
    owner_id: UUID,
    query: str,
    top_k: int = 10,
) -> list[MemoryBase]:
    """
    벡터 검색 + Retrieval Score 계산으로 관련 기억을 반환합니다.

    Args:
        owner_id: 기억 소유자 ID (participant.id)
        query: 현재 대화 컨텍스트 (임베딩 쿼리로 사용)
        top_k: 반환할 최대 기억 개수

    Returns:
        Retrieval Score 내림차순 정렬된 MemoryBase 리스트
        (score = α*Recency + β*Memory_Strength + γ*Relevance)
    """
    ...
```

### 아키텍처 원칙

- 의존성 방향은 `api → workflow → services → database` 단방향만 허용
- LLM Provider는 `LLMProvider` Protocol 구현 후 `register_provider()`로 등록 — 기존 코드 수정 없이 플러그인 추가
- 에이전트는 독립적으로 동작하고 LangGraph 공유 상태로 협력 (느슨한 결합 유지)
- 이벤트 기반 아키텍처 적용

### Memory 관련

- 모든 Memory Object 필수 필드: `importance_score`, `memory_strength`, `access_count`, `created_at`, `last_access_time`
- Observation은 원본 메시지와 **별도** 저장 (검색 최적화 목적)
- Reflection은 "요약"이 아닌 "상위 의미 추론" — 사용자 패턴/선호/목표 추론
- Importance Score는 LLM이 자동 평가 → 초기 Memory Strength로 사용
- Reflection 트리거: 최근 Observation들의 `importance_score` 누적 합 ≥ 임계값
- User Portrait 업데이트: 새 Reflection 일정 개수 이상 축적 시
- Memory Suppression: 삭제 대신 `disclosure_weight` 낮춰 억제, Retrieval Score에 `base_score * disclosure_weight` 적용
- 컨텍스트 윈도우 초과 시: `Memory_Strength` 낮은 기억부터 제거, 최근 5개 메시지는 유지

### 대화 정책 (Planning Agent 내부 적용)

- 연속 질문 최대 1회 (`max_consecutive_questions=1`)
- Short Reaction은 강한 신호(감정 공유, 놀람, 강한 동의)시에만 조건부 포함
- Anti-Sycophancy: 감정 공감(`emotion_validate=True`)과 사실 동조는 별개 — Loaded Premise 감지 시 부드럽게 수정
- Repair 순서: acknowledge → restate → correct → continue
- Formality는 캐릭터 system prompt에서 고정, 감정 강도 ≥ `formality_deviation_threshold`(0.7)시에만 일시적 이탈
- `ConversationPolicy`는 frozen dataclass로 LangGraph 초기화 시 주입 — 별도 노드로 만들지 않음

### 비동기 처리

- 모든 DB/LLM 호출은 `async/await` 사용
- WebSocket 스트리밍은 `AsyncIterator[str]`로 처리

### 보안

- LLM API 전송 전 PII 마스킹 필수
- 사용자별 DB 쿼리 격리 (`person_id` 필터 필수)
- WebSocket TLS/SSL 적용

### 에러 처리

- 벡터 검색 실패 시 tag 기반 keyword 검색으로 fallback
- LLM 호출 실패 시 다른 Provider로 자동 전환, 최대 3회 재시도
- Portrait 업데이트 실패 시 이전 Portrait 유지 (무중단)
