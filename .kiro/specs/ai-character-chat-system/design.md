# Design Document: AI Character Chat System

> 이 파일은 인덱스입니다. 각 섹션의 상세 내용은 `design/` 폴더의 개별 파일을 참조하세요.

## 문서 구조

| 파일 | 내용 |
|------|------|
| [00_overview.md](design/00_overview.md) | 시스템 개요, 기술 스택, 레이어 아키텍처, Memory Stream 계층 구조 |
| [01_workflow.md](design/01_workflow.md) | LangGraph 메인 워크플로우, Chain Components, Subgraphs, WebSocket Server |
| [02_agents.md](design/02_agents.md) | 7개 에이전트 상세 설계, ConversationPolicy |
| [03_memory_system.md](design/03_memory_system.md) | Memory Stream, Retrieval Engine, Memory Evolution Engine, User Portrait Manager |
| [04_data_models.md](design/04_data_models.md) | DB 스키마 (PostgreSQL + pgvector), 데이터 흐름 다이어그램 |
| [05_llm_adapter.md](design/05_llm_adapter.md) | LLM 추상화 계층, Provider 플러그인 구조 |
| [06_patterns.md](design/06_patterns.md) | 공통 구현 패턴 (Retrieval, Portrait, Memory Evolution 등) |
| [07_error_handling.md](design/07_error_handling.md) | 에러 처리 전략 (Memory, LLM, WebSocket) |
| [08_testing.md](design/08_testing.md) | 테스트 전략 (Unit, Integration, Performance, PBT) |

## 참고 자료 (References)

> 참고 자료는 `.kiro/specs/ai-character-chat-system/references/` 폴더에 있습니다.

| 파일 | 설명 | 관련 설계 문서 |
|------|------|---------------|
| [ene.md](references/ene.md) | ENE 프로젝트의 목적과 지향점 | 00_overview, 02_agents |
| [park2023Generative_ene.md](references/park2023Generative_ene.md) | Generative Agents 논문 요약 및 적용 방안 | 00_overview, 03_memory_system |
| [memoryBank_ene.md](references/memoryBank_ene.md) | MemoryBank 논문 요약 및 적용 방안 | 03_memory_system |
| [ene.sql](references/ene.sql) | 데이터베이스 DDL 원본 | 04_data_models |
| [database_schema.md](references/database_schema.md) | DB 스키마 설계 문서 | 04_data_models |
| [conversation_policy_research.md](references/conversation_policy_research.md) | 대화 정책 연구 자료 | 02_agents |
| [aws_architecture.md](references/aws_architecture.md) | AWS 배포 아키텍처 | 00_overview |
| [privacy_policy_research.md](references/privacy_policy_research.md) | 개인정보 보호 정책 연구 | 07_error_handling |
| [env_example.md](references/env_example.md) | 환경 변수 예시 | - |
| [project_structure.md](references/project_structure.md) | 프로젝트 구조 가이드 | - |

## 핵심 개념 요약

### 대화 흐름
```
사용자 메시지 → Autonomous Behavior → Memory Retrieval → Emotion Analysis
    → Dialogue Planning → Message Generation → Memory Save → 응답 반환
```

### Memory 계층
```
Message → Observation → Episode → Reflection → User Portrait
```

### Retrieval Score
```
Retrieval_Score = α * Recency + β * Memory_Strength + γ * Relevance
```

### Memory Strength
```
Memory_Strength(t) = Initial_Strength * e^(-decay_rate * t) + Σ(reinforcement_per_access)
```
