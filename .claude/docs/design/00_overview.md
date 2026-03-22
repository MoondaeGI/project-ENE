# Overview & Architecture

## 시스템 개요

AI Character Chat System은 사용자와 장기적인 관계를 형성하고, 축적된 맥락을 바탕으로 자연스럽고 의미 있는 대화를 제공하는 memory-based agent 시스템입니다.

핵심 개념:

- **Memory Stream**: Generative Agents 아키텍처 기반, 모든 대화를 Observation으로 변환하여 시간순 저장
- **Advanced Retrieval**: Recency + Memory_Strength + Relevance 가중합 기반 검색
- **Reflection**: 원시 기억으로부터 상위 의미를 추론하는 시스템
- **Planning**: 대화 목표를 계획하는 메커니즘

## 실행 방법

```bash
# 의존성 설치
poetry install

# 환경 변수 설정
cp .env.example .env

# DB 초기화
poetry run python scripts/setup_db.py

# 개발 서버 실행
poetry run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Docker
docker-compose up --build
```

## 기술 스택

| 분류            | 기술                                                |
| --------------- | --------------------------------------------------- |
| Language        | Python 3.11+                                        |
| Web Framework   | FastAPI (비동기, WebSocket)                         |
| Multi-Agent     | LangGraph (상태 기반 오케스트레이션)                |
| LLM Integration | LangChain                                           |
| Database        | PostgreSQL + pgvector                               |
| Deployment      | AWS Cloud                                           |
| LLM Providers   | OpenAI, Anthropic, Google Gemini, Ollama, LM Studio |

## 시스템 레이어 구조

```
Communication Layer  → FastAPI WebSocket Server
Workflow Layer       → LangGraph StateGraph (메인 + 서브그래프)
LLM Abstraction      → LangChain LLM Adapter (Strategy 패턴)
Data Layer           → PostgreSQL + pgvector
```

```
api → workflow → services → database
               ↘ models ↗
core (모든 레이어에서 사용)
background → services → database
```

## Memory Stream 계층 구조

```
원본 Message → Observation → Episode → Reflection → User Portrait
```

- **Message**: 원본 대화 메시지 (사용자/AI 발화)
- **Observation**: 검색 친화적으로 재표현된 사건 ("사용자가 X에 관심을 보임")
- **Episode**: 의미 있는 사건 묶음 (목적, 전환점, 결론, 감정 변화 포함)
- **Reflection**: 원시 기억으로부터 추론된 상위 의미 ("사용자는 Y를 선호한다")
- **User Portrait**: Reflection들로부터 생성된 사용자 프로필

## Retrieval Score 공식

```
Retrieval_Score = α * Recency + β * Memory_Strength + γ * Relevance
기본값: α=0.3, β=0.4, γ=0.3
```

- **Recency**: 최근 접근 시간 기반 (exponential decay, `-0.01 * hours_since_access`)
- **Memory_Strength**: `Initial_Strength * e^(-decay_rate * t) + Σ(reinforcement_per_access)`
- **Relevance**: 현재 쿼리와의 의미적 유사도 (벡터 임베딩 코사인 유사도)
