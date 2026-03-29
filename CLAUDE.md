# AI Character Chat System

Memory-based AI 캐릭터 채팅 시스템. 사용자와 장기적 관계를 형성하고 축적된 맥락으로 자연스러운 대화를 제공하는 **multi-agent 시스템**.

## 기술 스택

| 분류 | 기술 |
| --- | --- |
| Language | Python 3.11+ |
| Web Framework | FastAPI (비동기, WebSocket) |
| Multi-Agent | LangGraph (StateGraph 기반) |
| LLM Integration | LangChain |
| Database | PostgreSQL + pgvector (HNSW, VECTOR(1536)) |
| Deployment | AWS Cloud |
| Context Limit | 200,000 토큰 |

LLM Provider (현재): OpenAI / 추후 추가 예정: Anthropic, Google Gemini, Ollama, LM Studio

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

| 문서 | 내용 |
| --- | --- |
| [requirements.md](.claude/docs/requirements.md) | 요구사항 Req 1~3.5 (LLM·메모리 핵심) |
| [requirements_behavior.md](.claude/docs/requirements_behavior.md) | 요구사항 Req 3.7~11 (대화·감정·인프라) |
| [tasks.md](.claude/docs/tasks.md) | 구현 태스크 목록 및 현황 |
| [design/00_overview.md](.claude/docs/design/00_overview.md) | 시스템 개요, Retrieval Score 공식 |
| [design/01_workflow.md](.claude/docs/design/01_workflow.md) | LangGraph 워크플로우, Chain/Subgraph |
| [design/02_agents.md](.claude/docs/design/02_agents.md) | 에이전트 목록 + Dialogue·Emotion·Planning Agent |
| [design/02_agents_detail.md](.claude/docs/design/02_agents_detail.md) | Retrieval·Topic·ConversationPolicy |
| [design/03_memory_system.md](.claude/docs/design/03_memory_system.md) | Memory Stream, Retrieval, Evolution |
| [design/04_data_models.md](.claude/docs/design/04_data_models.md) | DB 스키마 초기 설계 (핵심 테이블) |
| [design/04_data_models_supporting.md](.claude/docs/design/04_data_models_supporting.md) | DB 스키마 초기 설계 (보조 테이블) |
| [design/05_llm_adapter.md](.claude/docs/design/05_llm_adapter.md) | LLMProvider Protocol, LLMAdapter |
| [design/06_patterns.md](.claude/docs/design/06_patterns.md) | 핵심 코드 패턴 모음 |
| [design/07_error_handling.md](.claude/docs/design/07_error_handling.md) | 에러 처리 전략 |
| [design/08_testing.md](.claude/docs/design/08_testing.md) | 테스트 전략 및 성능 목표 |
| [design/09_project_structure.md](.claude/docs/design/09_project_structure.md) | 전체 디렉터리 구조, 레이어별 파일 목록 |
| [design/09_project_structure_examples.md](.claude/docs/design/09_project_structure_examples.md) | 주요 파일 코드 예시 |
| [design/10_database_schema.md](.claude/docs/design/10_database_schema.md) | DDL 최신 (대화자·감정·메모리 테이블) |
| [design/10_database_schema_user.md](.claude/docs/design/10_database_schema_user.md) | DDL 최신 (사용자 이해 테이블) + ERD |
| [design/11_aws_architecture.md](.claude/docs/design/11_aws_architecture.md) | AWS 배포 아키텍처, 비용, 확장 포인트 |

## 코딩 가이드라인

@.claude/rules/code-style.md

## Git & 테스트

@.claude/rules/git-convention.md
