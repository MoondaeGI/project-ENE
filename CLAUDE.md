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

LLM Provider (현재): OpenAI / 추후 추가 예정: Anthropic, Google Gemini, Ollama, LM Studio

## 아키텍처

```text
api → workflow → services → database   (단방향 의존)
               ↘ models ↗
core (모든 레이어), background → services → database
```

**메인 워크플로우**: Autonomous Behavior → Memory Retrieval → Emotion Analysis → Dialogue Planning → Message Generation → Memory Save

**Memory Stream 계층**: `Message → Observation → Episode → Reflection → User Portrait`

## 아키텍처 원칙

- 의존성 방향은 `api → workflow → services → database` 단방향만 허용
- LLM Provider는 `LLMProvider` Protocol 구현 후 `register_provider()`로 등록 — 기존 코드 수정 없이 플러그인 추가
- 에이전트는 독립적으로 동작하고 LangGraph 공유 상태로 협력 (느슨한 결합 유지)
- 이벤트 기반 아키텍처 적용

## 비동기 처리

- 모든 DB/LLM 호출은 `async/await` 사용
- WebSocket 스트리밍은 `AsyncIterator[str]`로 처리

## 에러 처리

- 벡터 검색 실패 시 tag 기반 keyword 검색으로 fallback
- LLM 호출 실패 시 다른 Provider로 자동 전환, 최대 3회 재시도
- Portrait 업데이트 실패 시 이전 Portrait 유지 (무중단)

## 참고 문서

`.claude/docs/` 안에 있습니다.

| 문서                                                                                            | 내용                                            |
| ----------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| [requirements.md](.claude/docs/requirements.md)                                                 | 요구사항 Req 1~3.5 (LLM·메모리 핵심)            |
| [requirements_behavior.md](.claude/docs/requirements_behavior.md)                               | 요구사항 Req 3.7~11 (대화·감정·인프라)          |
| [tasks.md](.claude/docs/tasks.md)                                                               | 구현 태스크 목록 및 현황                        |
| [design/00_overview.md](.claude/docs/design/00_overview.md)                                     | 시스템 개요, Retrieval Score 공식               |
| [design/01_workflow.md](.claude/docs/design/01_workflow.md)                                     | LangGraph 워크플로우, Chain/Subgraph            |
| [design/02_agents.md](.claude/docs/design/02_agents.md)                                         | 에이전트 목록 + Dialogue·Emotion·Planning Agent |
| [design/02_agents_detail.md](.claude/docs/design/02_agents_detail.md)                           | Retrieval·Topic·ConversationPolicy              |
| [design/03_memory_system.md](.claude/docs/design/03_memory_system.md)                           | Memory Stream, Retrieval, Evolution             |
| [design/04_data_models.md](.claude/docs/design/04_data_models.md)                               | DB 스키마 초기 설계 (핵심 테이블)               |
| [design/04_data_models_supporting.md](.claude/docs/design/04_data_models_supporting.md)         | DB 스키마 초기 설계 (보조 테이블)               |
| [design/05_llm_adapter.md](.claude/docs/design/05_llm_adapter.md)                               | LLMProvider Protocol, LLMAdapter                |
| [design/06_patterns.md](.claude/docs/design/06_patterns.md)                                     | 핵심 코드 패턴 모음                             |
| [design/07_error_handling.md](.claude/docs/design/07_error_handling.md)                         | 에러 처리 전략                                  |
| [design/08_testing.md](.claude/docs/design/08_testing.md)                                       | 테스트 전략 및 성능 목표                        |
| [design/09_project_structure.md](.claude/docs/design/09_project_structure.md)                   | 전체 디렉터리 구조, 레이어별 파일 목록          |
| [design/09_project_structure_examples.md](.claude/docs/design/09_project_structure_examples.md) | 주요 파일 코드 예시                             |
| [design/10_database_schema.md](.claude/docs/design/10_database_schema.md)                       | DDL 최신 (대화자·감정·메모리 테이블)            |
| [design/10_database_schema_user.md](.claude/docs/design/10_database_schema_user.md)             | DDL 최신 (사용자 이해 테이블) + ERD             |
| [design/11_aws_architecture.md](.claude/docs/design/11_aws_architecture.md)                     | AWS 배포 아키텍처, 비용, 확장 포인트            |
