# Project Directory Structure

## Directory Structure

```
ai-character-chat-system/
├── src/
│   ├── api/                          # API Layer (FastAPI)
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI 앱 진입점
│   │   ├── websocket.py              # WebSocket 엔드포인트
│   │   ├── routes/                   # REST API 라우트
│   │   │   ├── health.py             # 헬스체크
│   │   │   ├── users.py              # 사용자 관리
│   │   │   └── admin.py              # 관리자 API
│   │   ├── middleware/
│   │   │   ├── auth.py               # 인증
│   │   │   ├── cors.py               # CORS
│   │   │   └── logging.py            # 로깅
│   │   └── dependencies.py           # FastAPI 의존성
│   │
│   ├── workflow/                     # Workflow Layer (LangGraph)
│   │   ├── main_workflow.py          # 메인 워크플로우
│   │   ├── state.py                  # 공유 상태 정의 (ConversationState)
│   │   ├── nodes/                    # 단순 노드들
│   │   │   ├── autonomous_behavior.py
│   │   │   ├── memory_retrieval.py
│   │   │   ├── dialogue_planning.py
│   │   │   ├── policy_check.py
│   │   │   └── message_generation.py
│   │   └── subgraphs/                # 복잡한 서브그래프들
│   │       ├── emotion_analysis.py
│   │       └── memory_save.py
│   │
│   ├── services/                     # Business Logic Layer
│   │   ├── memory/
│   │   │   ├── memory_stream.py      # Memory Stream 관리
│   │   │   ├── retrieval_engine.py   # 검색 엔진
│   │   │   ├── reflection_generator.py
│   │   │   ├── episode_manager.py
│   │   │   └── memory_evolution.py   # Memory Evolution Engine
│   │   ├── emotion/
│   │   │   ├── emotion_analyzer.py
│   │   │   └── emotion_tracker.py
│   │   ├── portrait/
│   │   │   ├── portrait_manager.py
│   │   │   └── trait_analyzer.py
│   │   ├── dialogue/
│   │   │   ├── planner.py
│   │   │   └── policy_checker.py
│   │   └── llm/
│   │       ├── adapter.py            # LLM Adapter
│   │       ├── providers/
│   │       │   ├── base.py           # 추상 인터페이스
│   │       │   ├── openai_provider.py
│   │       │   ├── anthropic_provider.py
│   │       │   ├── google_provider.py
│   │       │   └── ollama_provider.py
│   │       └── prompts/              # 프롬프트 템플릿
│   │           ├── character_persona.py
│   │           ├── emotion_analysis.py
│   │           └── reflection.py
│   │
│   ├── models/                       # Data Models
│   │   ├── domain/                   # 도메인 모델
│   │   │   ├── participant.py
│   │   │   ├── message.py
│   │   │   ├── memory.py
│   │   │   ├── emotion.py
│   │   │   └── portrait.py
│   │   └── dto/                      # Data Transfer Objects
│   │       ├── request.py
│   │       └── response.py
│   │
│   ├── database/                     # Data Layer
│   │   ├── connection.py             # DB 연결 관리
│   │   ├── models.py                 # SQLAlchemy ORM 모델
│   │   ├── repositories/             # Repository 패턴
│   │   │   ├── base.py
│   │   │   ├── participant_repo.py
│   │   │   ├── message_repo.py
│   │   │   ├── memory_repo.py
│   │   │   ├── emotion_repo.py
│   │   │   └── portrait_repo.py
│   │   ├── migrations/               # Alembic 마이그레이션
│   │   │   ├── versions/
│   │   │   │   └── 0001_initial_schema.py
│   │   │   └── env.py
│   │   └── seeds/
│   │       └── initial_character.py  # 초기 캐릭터 데이터
│   │
│   ├── core/                         # Core Utilities
│   │   ├── config.py                 # 설정 관리 (pydantic-settings)
│   │   ├── logging.py                # 로깅 설정
│   │   ├── exceptions.py             # 커스텀 예외
│   │   └── utils/
│   │       ├── embedding.py          # 임베딩 생성
│   │       ├── vector_search.py      # 벡터 검색
│   │       └── time_utils.py
│   │
│   └── background/                   # Background Tasks
│       ├── scheduler.py              # 스케줄러 (APScheduler)
│       ├── tasks/
│       │   ├── memory_decay.py       # 망각 곡선 적용 (매일 자정)
│       │   └── portrait_update.py    # User Portrait 업데이트 (매일 03:00)
│       └── workers.py
│
├── tests/
│   ├── conftest.py                   # pytest 설정 (shared fixtures)
│   ├── unit/
│   │   ├── test_memory_stream.py
│   │   ├── test_retrieval_engine.py
│   │   ├── test_emotion_analyzer.py
│   │   └── test_llm_adapter.py
│   ├── integration/
│   │   ├── test_workflow.py
│   │   ├── test_api.py
│   │   └── test_websocket.py
│   └── e2e/
│       └── test_conversation_flow.py
│
├── scripts/
│   ├── setup_db.py                   # DB 초기화 (pgvector 확장 + 마이그레이션)
│   ├── seed_data.py                  # 데이터 시딩
│   └── migrate.py                    # 마이그레이션 실행
│
├── config/
│   ├── development.yaml
│   ├── production.yaml
│   └── test.yaml
│
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.dev.yml
│
├── .env.example
├── .gitignore
├── pyproject.toml
└── alembic.ini
```

## Layer별 책임

| Layer | 경로 | 책임 |
|-------|------|------|
| API | `src/api/` | HTTP/WebSocket 엔드포인트, 인증, 요청 검증 |
| Workflow | `src/workflow/` | LangGraph 대화 흐름 제어, 노드 간 상태 전달 |
| Services | `src/services/` | 핵심 비즈니스 로직, 도메인 규칙 적용 |
| Models | `src/models/` | 데이터 구조 정의, Pydantic 유효성 검증 |
| Database | `src/database/` | DB 연결 관리, Repository 패턴, 마이그레이션 |
| Core | `src/core/` | 설정, 로깅, 커스텀 예외, 공통 유틸리티 |
| Background | `src/background/` | 주기적 작업 (망각 곡선, Portrait 업데이트) |

## 주요 파일 예시

### `src/api/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import health, users, admin
from src.api.websocket import websocket_endpoint
from src.core.config import settings

app = FastAPI(title="AI Character Chat System", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.add_websocket_route("/ws/{user_id}", websocket_endpoint)

@app.on_event("startup")
async def startup_event():
    from src.database.connection import init_db
    from src.background.scheduler import start_scheduler
    await init_db()
    start_scheduler()
```

### `src/workflow/main_workflow.py`

```python
from langgraph.graph import StateGraph, END
from src.workflow.state import ConversationState

def create_main_workflow():
    workflow = StateGraph(ConversationState)

    workflow.add_node("autonomous_behavior", autonomous_behavior.node)
    workflow.add_node("memory_retrieval", memory_retrieval.node)
    workflow.add_node("emotion_analysis", emotion_analysis.create_subgraph())
    workflow.add_node("dialogue_planning", dialogue_planning.node)
    workflow.add_node("message_generation", message_generation.node)
    workflow.add_node("memory_save", memory_save.create_subgraph())

    workflow.set_entry_point("autonomous_behavior")
    workflow.add_conditional_edges(
        "autonomous_behavior",
        lambda state: "respond" if state["should_respond"] else "silence",
        {"respond": "memory_retrieval", "silence": END}
    )
    workflow.add_edge("memory_retrieval", "emotion_analysis")
    workflow.add_edge("emotion_analysis", "dialogue_planning")
    workflow.add_edge("dialogue_planning", "message_generation")
    workflow.add_edge("message_generation", "memory_save")
    workflow.add_edge("memory_save", END)

    return workflow.compile()

app = create_main_workflow()
```

### `src/core/config.py`

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    DEFAULT_LLM_PROVIDER: str = "openai"
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    EMBEDDING_DIMENSION: int = 1536
    MEMORY_DECAY_RATE: float = 0.01
    REFLECTION_THRESHOLD: float = 10.0
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
```

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
