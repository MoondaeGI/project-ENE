# Project Directory Structure

## Overview

AI Character Chat System의 프로젝트 디렉토리 구조입니다. FastAPI + LangGraph 기반의 멀티 에이전트 시스템으로, 계층적이고 확장 가능한 구조를 따릅니다.

---

## Directory Structure

```
ai-character-chat-system/
├── src/
│   ├── api/                          # API Layer (FastAPI)
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI 앱 진입점
│   │   ├── websocket.py              # WebSocket 엔드포인트
│   │   ├── routes/                   # REST API 라우트
│   │   │   ├── __init__.py
│   │   │   ├── health.py             # 헬스체크
│   │   │   ├── users.py              # 사용자 관리
│   │   │   └── admin.py              # 관리자 API
│   │   ├── middleware/               # 미들웨어
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # 인증
│   │   │   ├── cors.py               # CORS
│   │   │   └── logging.py            # 로깅
│   │   └── dependencies.py           # FastAPI 의존성
│   │
│   ├── workflow/                     # Workflow Layer (LangGraph)
│   │   ├── __init__.py
│   │   ├── main_workflow.py          # 메인 워크플로우
│   │   ├── state.py                  # 공유 상태 정의
│   │   ├── nodes/                    # 단순 노드들
│   │   │   ├── __init__.py
│   │   │   ├── autonomous_behavior.py
│   │   │   ├── memory_retrieval.py
│   │   │   ├── dialogue_planning.py
│   │   │   ├── policy_check.py
│   │   │   └── message_generation.py
│   │   └── subgraphs/                # 복잡한 서브그래프들
│   │       ├── __init__.py
│   │       ├── emotion_analysis.py
│   │       └── memory_save.py
│   │
│   ├── services/                     # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── memory/                   # 메모리 관리
│   │   │   ├── __init__.py
│   │   │   ├── memory_stream.py      # Memory Stream 관리
│   │   │   ├── retrieval_engine.py   # 검색 엔진
│   │   │   ├── reflection_generator.py
│   │   │   ├── episode_manager.py
│   │   │   └── memory_evolution.py   # Memory Evolution Engine
│   │   ├── emotion/                  # 감정 관리
│   │   │   ├── __init__.py
│   │   │   ├── emotion_analyzer.py
│   │   │   └── emotion_tracker.py
│   │   ├── portrait/                 # User Portrait
│   │   │   ├── __init__.py
│   │   │   ├── portrait_manager.py
│   │   │   └── trait_analyzer.py
│   │   ├── dialogue/                 # 대화 관리
│   │   │   ├── __init__.py
│   │   │   ├── planner.py
│   │   │   └── policy_checker.py
│   │   └── llm/                      # LLM 통합
│   │       ├── __init__.py
│   │       ├── adapter.py            # LLM Adapter
│   │       ├── providers/            # LLM 제공자들
│   │       │   ├── __init__.py
│   │       │   ├── base.py           # 추상 인터페이스
│   │       │   ├── openai_provider.py
│   │       │   ├── anthropic_provider.py
│   │       │   ├── google_provider.py
│   │       │   └── ollama_provider.py
│   │       └── prompts/              # 프롬프트 템플릿
│   │           ├── __init__.py
│   │           ├── character_persona.py
│   │           ├── emotion_analysis.py
│   │           └── reflection.py
│   │
│   ├── models/                       # Data Models
│   │   ├── __init__.py
│   │   ├── domain/                   # 도메인 모델
│   │   │   ├── __init__.py
│   │   │   ├── participant.py
│   │   │   ├── message.py
│   │   │   ├── memory.py
│   │   │   ├── emotion.py
│   │   │   └── portrait.py
│   │   └── dto/                      # Data Transfer Objects
│   │       ├── __init__.py
│   │       ├── request.py
│   │       └── response.py
│   │
│   ├── database/                     # Data Layer
│   │   ├── __init__.py
│   │   ├── connection.py             # DB 연결 관리
│   │   ├── repositories/             # Repository 패턴
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── participant_repo.py
│   │   │   ├── message_repo.py
│   │   │   ├── memory_repo.py
│   │   │   ├── emotion_repo.py
│   │   │   └── portrait_repo.py
│   │   ├── migrations/               # DB 마이그레이션
│   │   │   ├── versions/
│   │   │   └── env.py
│   │   └── seeds/                    # 초기 데이터
│   │       └── initial_character.py
│   │
│   ├── core/                         # Core Utilities
│   │   ├── __init__.py
│   │   ├── config.py                 # 설정 관리
│   │   ├── logging.py                # 로깅 설정
│   │   ├── exceptions.py             # 커스텀 예외
│   │   └── utils/                    # 유틸리티
│   │       ├── __init__.py
│   │       ├── embedding.py          # 임베딩 생성
│   │       ├── vector_search.py      # 벡터 검색
│   │       └── time_utils.py
│   │
│   └── background/                   # Background Tasks
│       ├── __init__.py
│       ├── scheduler.py              # 스케줄러
│       ├── tasks/
│       │   ├── __init__.py
│       │   ├── memory_decay.py       # 망각 곡선 적용
│       │   └── portrait_update.py    # User Portrait 업데이트
│       └── workers.py
│
├── tests/                            # 테스트
│   ├── __init__.py
│   ├── conftest.py                   # pytest 설정
│   ├── unit/                         # 단위 테스트
│   │   ├── test_memory_stream.py
│   │   ├── test_retrieval_engine.py
│   │   ├── test_emotion_analyzer.py
│   │   └── test_llm_adapter.py
│   ├── integration/                  # 통합 테스트
│   │   ├── test_workflow.py
│   │   ├── test_api.py
│   │   └── test_websocket.py
│   └── e2e/                          # E2E 테스트
│       └── test_conversation_flow.py
│
├── scripts/                          # 유틸리티 스크립트
│   ├── setup_db.py                   # DB 초기화
│   ├── seed_data.py                  # 데이터 시딩
│   └── migrate.py                    # 마이그레이션 실행
│
├── config/                           # 설정 파일
│   ├── development.yaml
│   ├── production.yaml
│   └── test.yaml
│
├── docker/                           # Docker 관련
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.dev.yml
│
├── docs/                             # 문서
│   ├── api/                          # API 문서
│   ├── architecture/                 # 아키텍처 문서
│   └── deployment/                   # 배포 가이드
│
├── .env.example                      # 환경 변수 예시
├── .gitignore
├── pyproject.toml                    # Python 프로젝트 설정
├── poetry.lock                       # 의존성 잠금
├── README.md
└── requirements.txt                  # pip 의존성 (선택)
```

---

## Layer별 상세 설명

### 1. API Layer (`src/api/`)

FastAPI 기반의 HTTP/WebSocket 엔드포인트를 제공합니다.

**주요 파일**:
- `main.py`: FastAPI 앱 생성, 라우터 등록, 미들웨어 설정
- `websocket.py`: WebSocket 연결 관리, 메시지 송수신
- `routes/`: REST API 엔드포인트 (헬스체크, 사용자 관리 등)
- `middleware/`: 인증, CORS, 로깅 등

**책임**:
- HTTP 요청/응답 처리
- WebSocket 연결 관리
- 인증/인가
- 요청 검증

### 2. Workflow Layer (`src/workflow/`)

LangGraph 기반의 대화 워크플로우를 관리합니다.

**주요 파일**:
- `main_workflow.py`: 메인 StateGraph 정의
- `state.py`: ConversationState 정의
- `nodes/`: 단순 노드 구현
- `subgraphs/`: 복잡한 서브그래프 구현

**책임**:
- 대화 흐름 제어
- 노드 간 상태 전달
- 조건부 분기 처리

### 3. Services Layer (`src/services/`)

비즈니스 로직을 담당합니다.

**주요 디렉토리**:
- `memory/`: Memory Stream, Retrieval, Reflection, Episode 관리
- `emotion/`: 감정 분석 및 추적
- `portrait/`: User Portrait 생성 및 관리
- `dialogue/`: 대화 계획 및 정책 검사
- `llm/`: LLM 통합 및 프롬프트 관리

**책임**:
- 핵심 비즈니스 로직
- 도메인 규칙 적용
- 외부 서비스 통합 (LLM)

### 4. Models Layer (`src/models/`)

데이터 모델을 정의합니다.

**주요 디렉토리**:
- `domain/`: 도메인 엔티티 (Participant, Message, Memory 등)
- `dto/`: API 요청/응답 객체

**책임**:
- 데이터 구조 정의
- 유효성 검증 (Pydantic)
- 타입 안정성

### 5. Database Layer (`src/database/`)

데이터 영속성을 담당합니다.

**주요 디렉토리**:
- `repositories/`: Repository 패턴 구현
- `migrations/`: Alembic 마이그레이션
- `seeds/`: 초기 데이터

**책임**:
- DB 연결 관리
- CRUD 작업
- 트랜잭션 관리
- 마이그레이션

### 6. Core Layer (`src/core/`)

공통 유틸리티 및 설정을 제공합니다.

**주요 파일**:
- `config.py`: 환경 변수, 설정 관리
- `logging.py`: 로깅 설정
- `exceptions.py`: 커스텀 예외
- `utils/`: 임베딩, 벡터 검색 등

**책임**:
- 설정 관리
- 로깅
- 공통 유틸리티

### 7. Background Layer (`src/background/`)

백그라운드 작업을 처리합니다.

**주요 파일**:
- `scheduler.py`: 스케줄러 (APScheduler)
- `tasks/`: 주기적 작업 (망각 곡선, Portrait 업데이트)

**책임**:
- 주기적 작업 실행
- 비동기 작업 처리

---

## 주요 파일 예시

### `src/api/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import health, users, admin
from src.api.websocket import websocket_endpoint
from src.api.middleware.logging import LoggingMiddleware
from src.core.config import settings
from src.core.logging import setup_logging

# 로깅 설정
setup_logging()

# FastAPI 앱 생성
app = FastAPI(
    title="AI Character Chat System",
    version="1.0.0",
    description="Memory-based agent system"
)

# 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

# 라우터 등록
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

# WebSocket
app.add_websocket_route("/ws/{user_id}", websocket_endpoint)

@app.on_event("startup")
async def startup_event():
    """앱 시작 시 초기화"""
    from src.database.connection import init_db
    from src.background.scheduler import start_scheduler
    
    await init_db()
    start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    """앱 종료 시 정리"""
    from src.database.connection import close_db
    from src.background.scheduler import stop_scheduler
    
    await close_db()
    stop_scheduler()
```

### `src/workflow/main_workflow.py`

```python
from langgraph.graph import StateGraph, END

from src.workflow.state import ConversationState
from src.workflow.nodes import (
    autonomous_behavior,
    memory_retrieval,
    dialogue_planning,
    policy_check,
    message_generation
)
from src.workflow.subgraphs import (
    emotion_analysis,
    memory_save
)

def create_main_workflow():
    """메인 워크플로우 생성"""
    workflow = StateGraph(ConversationState)
    
    # 노드 추가
    workflow.add_node("autonomous_behavior", autonomous_behavior.node)
    workflow.add_node("memory_retrieval", memory_retrieval.node)
    workflow.add_node("emotion_analysis", emotion_analysis.create_subgraph())
    workflow.add_node("dialogue_planning", dialogue_planning.node)
    workflow.add_node("policy_check", policy_check.node)
    workflow.add_node("message_generation", message_generation.node)
    workflow.add_node("memory_save", memory_save.create_subgraph())
    
    # 흐름 정의
    workflow.set_entry_point("autonomous_behavior")
    
    workflow.add_conditional_edges(
        "autonomous_behavior",
        lambda state: "respond" if state["should_respond"] else "silence",
        {
            "respond": "memory_retrieval",
            "silence": END
        }
    )
    
    workflow.add_edge("memory_retrieval", "emotion_analysis")
    workflow.add_edge("emotion_analysis", "dialogue_planning")
    workflow.add_edge("dialogue_planning", "policy_check")
    workflow.add_edge("policy_check", "message_generation")
    workflow.add_edge("message_generation", "memory_save")
    workflow.add_edge("memory_save", END)
    
    return workflow.compile()

# 전역 워크플로우 인스턴스
app = create_main_workflow()
```

### `src/core/config.py`

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # 앱 설정
    APP_NAME: str = "AI Character Chat System"
    DEBUG: bool = False
    
    # 데이터베이스
    DATABASE_URL: str
    
    # LLM
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    DEFAULT_LLM_PROVIDER: str = "openai"
    
    # 벡터 임베딩
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    EMBEDDING_DIMENSION: int = 1536
    
    # Memory Evolution
    MEMORY_DECAY_RATE: float = 0.01
    REFLECTION_THRESHOLD: float = 10.0
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # 로깅
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

## 의존성 관리 (`pyproject.toml`)

```toml
[tool.poetry]
name = "ai-character-chat-system"
version = "1.0.0"
description = "Memory-based agent system"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.109.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
websockets = "^12.0"
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"

# LangChain & LangGraph
langchain = "^0.1.0"
langgraph = "^0.0.20"
langchain-openai = "^0.0.5"
langchain-anthropic = "^0.0.1"

# Database
asyncpg = "^0.29.0"
sqlalchemy = "^2.0.25"
alembic = "^1.13.0"
pgvector = "^0.2.4"

# Background Tasks
apscheduler = "^3.10.4"

# Utilities
python-dotenv = "^1.0.0"
pyyaml = "^6.0.1"
httpx = "^0.26.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.23.0"
pytest-cov = "^4.1.0"
black = "^24.0.0"
ruff = "^0.1.0"
mypy = "^1.8.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

---

## 실행 방법

### 개발 환경

```bash
# 의존성 설치
poetry install

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# DB 초기화
poetry run python scripts/setup_db.py

# 개발 서버 실행
poetry run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
# 빌드 및 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d
```

---

## 핵심 설계 원칙

1. **계층 분리**: API, Workflow, Service, Data 레이어 명확히 분리
2. **의존성 역전**: 상위 레이어가 하위 레이어에 의존 (인터페이스 기반)
3. **단일 책임**: 각 모듈은 하나의 책임만 가짐
4. **확장 가능**: 새로운 LLM Provider, 노드 추가 용이
5. **테스트 가능**: 각 레이어 독립적으로 테스트 가능
