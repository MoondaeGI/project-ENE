# AI Character Chat System - Project Context

## Project Overview

이 프로젝트는 단순한 챗봇이 아닌, 사용자와 장기적인 관계를 형성하고 축적된 맥락을 바탕으로 자연스럽고 의미 있는 대화를 제공하는 **memory-based agent 시스템**입니다.

핵심 목표:
- 일회성 응답이 아닌 **지속되는 관계** 형성
- 사용자의 관심사, 선호도, 작업 흐름, 감정 상태를 **기억하고 이해**
- "정보 제공자"가 아닌 **"생각을 함께 이어가는 동반자"**

## Technology Stack

### Core Technologies
- **Language**: Python 3.11+
- **Web Framework**: FastAPI (비동기 처리, WebSocket)
- **Multi-Agent Framework**: LangGraph (상태 기반 에이전트 오케스트레이션)
- **LLM Integration**: LangChain (LLM 추상화 계층)
- **Database**: PostgreSQL + pgvector (벡터 검색)
- **Deployment**: AWS Cloud

### LLM Providers (Plugin-based)
- **Cloud**: OpenAI, Anthropic, Google Gemini
- **Local**: Ollama, LM Studio, LocalAI

### System Constraints
- **Context Window**: 최대 200,000 토큰 (Claude Sonnet 4 기준)
- **Architecture**: 멀티 에이전트, 이벤트 기반, 플러그인 방식

## Key Architecture Concepts

### 1. Memory Stream Architecture (Generative Agents 기반)

모든 경험을 시간순으로 저장하는 계층적 메모리 구조:

```
원본 Message → Observation → Episode → Reflection → User Portrait
```

- **Message**: 원본 대화 메시지
- **Observation**: 검색 친화적으로 재표현된 사건 ("사용자가 X에 관심을 보임")
- **Episode**: 의미 있는 사건 묶음 (목적, 전환점, 결론, 감정 변화 포함)
- **Reflection**: 상위 의미 추론 ("사용자는 Y를 선호한다")
- **User Portrait**: Reflection들로부터 생성된 사용자 프로필 (선호도, 성격, 관심사, 대화 스타일)

### 2. Advanced Retrieval Mechanism (MemoryBank 기반)

검색 점수는 세 가지 요소의 가중합:

```
Retrieval_Score = α * Recency + β * Memory_Strength + γ * Relevance
```

- **Recency**: 최근 접근 시간 (exponential decay)
- **Memory_Strength**: 동적으로 변화하는 기억 강도 (접근 빈도에 따라 강화/망각)
- **Relevance**: 의미적 유사도 (벡터 임베딩 기반)

### 3. Memory Evolution (MemoryBank 기반)

기억은 시간과 접근 패턴에 따라 동적으로 변화:

- **Forgetting Curve**: 시간이 지남에 따라 기억 강도 감소 (Ebbinghaus 망각 곡선)
- **Memory Reinforcement**: 접근할 때마다 기억 강도 증가
- **Access Tracking**: 모든 기억 접근 이력 저장 (시간, 컨텍스트)

공식:
```
Memory_Strength(t) = Initial_Strength * e^(-decay_rate * t) + Σ(reinforcement_per_access)
```

### 4. Multi-Agent Orchestration

LangGraph를 사용한 7개 주요 에이전트:

1. **Dialogue Agent**: 대화 생성 및 응답 관리
2. **Emotion Agent**: 감정 분석 및 감정 상태 관리
3. **Planning Agent**: 대화 목표 설정 및 응답 전략 계획
4. **Retrieval Agent**: 관련 기억 검색 및 컨텍스트 구성
5. **Topic Recommender**: 사용자 관심사 분석 및 주제 추천
6. **User Portrait Manager**: 사용자 프로필 생성 및 업데이트
7. **Memory Evolution Engine**: 기억 강도 관리 및 망각 곡선 적용

### 5. Plugin-based LLM Abstraction

Strategy 패턴을 사용하여 런타임에 LLM 제공자를 동적으로 전환 가능.

## Core Design Principles

### Memory & Retrieval
- Observation은 원본 메시지와 별도로 저장 (검색 최적화)
- Reflection은 "요약"이 아닌 "상위 의미 추론"
- Episode는 단순 그룹화가 아닌 "의미 있는 사건 묶음"
- 모든 Memory Object는 `importance_score`, `memory_strength`, `access_count`, `created_at`, `last_access_time` 포함
- Memory Strength는 시간과 접근 패턴에 따라 동적으로 변화
- 망각 곡선 적용: 접근하지 않은 기억은 시간이 지남에 따라 약화
- 접근 강화: 기억을 검색할 때마다 강도 증가

### User Portrait
- Reflection들로부터 주기적으로 사용자 프로필 생성
- 선호도, 성격 특성, 관심사, 대화 스타일, 감정 패턴 포함
- 대화 응답 생성 시 User Portrait를 컨텍스트로 활용
- 시간이 지남에 따라 점진적으로 업데이트 (급격한 변화 방지)

### Conversation Policy
- 연속 질문 제한 (심문 같은 대화 방지)
- 짧은 반응 + 긴 설명 혼합
- 불완전한 대화에서도 흐름 파악 및 구조화
- 사용자의 사고를 다음 단계로 이어주는 역할

### Planning & Intention
- 대화 목표 설정 및 추적
- 응답 의도 계획: 설명/설계/위로/의사결정 보조
- 대화 종료 후 상태 관리 (미해결 질문, 다음 주제, 감정 상태)

### Emotion Management
- 다차원 감정 수치: 기쁨, 슬픔, 분노, 놀람, 두려움, 혐오
- 사용자 + AI 캐릭터 양쪽의 감정 상태 추적
- 감정에 따라 응답의 톤, 어휘, 문장 구조 조정

## Key Terminology

| Term | Description |
|------|-------------|
| **Memory_Stream** | 모든 경험을 시간순으로 저장하는 기억 흐름 |
| **Observation** | 검색 친화적으로 재표현된 사건 |
| **Importance_Score** | 각 기억의 초기 중요도 (0.0~1.0, LLM이 평가) |
| **Memory_Strength** | 동적으로 변화하는 기억 강도 (접근 빈도와 시간에 따라 변화) |
| **Retrieval_Score** | Recency + Memory_Strength + Relevance 가중합 |
| **Reflection** | 원시 기억으로부터 추론된 상위 의미 |
| **Episode** | 의미 있는 사건 묶음 (목적, 전환점, 결론 포함) |
| **User_Portrait** | Reflection들로부터 생성된 사용자 프로필 (선호도, 성격, 관심사, 대화 스타일) |
| **Memory_Evolution** | 시간과 접근 패턴에 따른 기억 강도의 동적 변화 |
| **Forgetting_Curve** | 시간이 지남에 따라 기억 강도가 감소하는 패턴 (Ebbinghaus 곡선) |
| **Dialogue_Intention** | 현재 대화의 목표와 응답 전략 |
| **Character_Persona** | 캐릭터의 성격, 말투, 행동 패턴 |

## Database Schema Highlights

### Core Tables
- `person`: 사용자 정보
- `message`: 원본 대화 메시지 (+ `access_count`)
- `observation`: 검색 친화적 사건 표현 (+ `access_count`)
- `episode`: 사건 묶음 (+ `episode_message` 매핑, + `access_count`)
- `reflection`: 상위 의미 추론 (+ `reflection_source` 매핑, + `access_count`)
- `user_portrait`: 사용자 프로필 (선호도, 성격, 관심사, 대화 스타일)
- `memory_access_history`: 기억 접근 이력 (시간, 컨텍스트)
- `tag`: 키워드 인덱싱 (+ 각 테이블별 매핑)
- `emotion_record`: 감정 이력
- `interest`: 사용자 관심사
- `dialogue_plan`: 대화 계획

### Vector Indexes (pgvector)
- `message_embedding_idx`: HNSW 인덱스
- `observation_embedding_idx`: HNSW 인덱스
- `episode_embedding_idx`: HNSW 인덱스
- `reflection_embedding_idx`: HNSW 인덱스

## Development Guidelines

### Code Organization
- 플러그인 방식으로 LLM Provider 추가
- 에이전트는 독립적으로 동작, 공유 상태로 협력
- 느슨한 결합 유지 (독립적 개발/배포)
- 이벤트 기반 아키텍처

### Memory Management
- Message → Observation 변환 시 검색 친화적으로 재표현
- Importance Score는 LLM이 자동 평가 (초기 Memory Strength로 사용)
- Reflection 생성 조건: Importance 누적 합이 임계값 도달
- User Portrait 생성 조건: 새로운 Reflection이 일정 개수 이상 축적
- Memory Strength 업데이트: 매 접근 시 강화, 백그라운드 작업으로 망각 곡선 적용
- 컨텍스트 윈도우 초과 시 Memory Strength 낮은 기억부터 제거

### Testing & Validation
- WebSocket 연결 재연결 테스트
- 벡터 검색 정확도 검증
- Retrieval Score 가중치 튜닝
- 감정 분석 정확도 평가

## Common Patterns

### Retrieval Pattern
```python
# 1. 쿼리 임베딩 생성
query_embedding = await embedding_service.embed(query)

# 2. Retrieval Score 계산
for memory in memories:
    recency = calculate_recency(memory.last_access_time)
    importance = memory.importance_score
    relevance = cosine_similarity(memory.embedding, query_embedding)
    memory.retrieval_score = α*recency + β*importance + γ*relevance

# 3. Top-K 선택 및 last_access_time 업데이트
top_memories = sorted(memories, key=lambda m: m.retrieval_score)[:k]
await update_access_times(top_memories)
```

### Reflection Generation Pattern
```python
# 1. Importance 누적 합 확인
importance_sum = sum(m.importance_score for m in recent_memories)

# 2. 임계값 도달 시 Reflection 생성
if importance_sum >= threshold:
    reflection = await llm.generate_reflection(recent_memories)
    reflection.importance_score = calculate_importance(reflection)
    await memory_stream.store_reflection(reflection)
```

### Agent Orchestration Pattern
```python
# LangGraph 상태 기반 흐름
state = ConversationState(user_id, message)

# 1. Retrieval Agent
state.retrieved_memories = await retrieval_agent.retrieve(state)

# 2. Emotion Agent
state.emotion_state = await emotion_agent.analyze(state)

# 3. Planning Agent
state.dialogue_intention = await planning_agent.plan(state)

# 4. Dialogue Agent
state.response = await dialogue_agent.generate(state)
```

## Reference Documents

프로젝트 참고 자료는 `.kiro/specs/ai-character-chat-system/references/` 폴더에 있습니다:

- `ene.md`: ENE 프로젝트의 목적과 지향점
- `park2023Generative_ene.md`: Generative Agents 논문 요약 및 적용 방안
- `ene.sql`: 데이터베이스 DDL (추후 design에서 구체화)

## Important Notes

### What This System IS
- Memory-based agent (장기 맥락 유지)
- 생각을 함께 이어가는 동반자
- 시간이 지날수록 개인화되는 AI

### What This System IS NOT
- 단순 질의응답 챗봇
- 일회성 정보 제공 도구
- 완벽한 인간 모방 (목표는 "이해하고 있다"고 느껴지는 수준)

### Security & Privacy
- DB 레벨 암호화 (at-rest)
- TLS/SSL 통신 암호화 (at-transit)
- 사용자별 데이터 격리
- 개인정보 마스킹 (LLM 전송 전)
- 데이터 보관 기간 정책

## Spec Files

- **Requirements**: `.kiro/specs/ai-character-chat-system/requirements.md`
- **Design**: `.kiro/specs/ai-character-chat-system/design.md`
- **Tasks**: `.kiro/specs/ai-character-chat-system/tasks.md` (생성 예정)
