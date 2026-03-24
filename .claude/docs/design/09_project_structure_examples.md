# Project Structure — 주요 파일 코드 예시

[← 09_project_structure.md](09_project_structure.md) 에서 이어지는 문서입니다.

## `src/api/main.py`

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

## `src/workflow/main_workflow.py`

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

## `src/core/config.py`

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: str = ""
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