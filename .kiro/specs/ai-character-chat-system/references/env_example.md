# Environment Variables (.env.example)

프로젝트 루트에 `.env.example` 파일을 생성하고, 실제 사용 시 `.env`로 복사하여 값을 채워넣습니다.

```bash
# .env.example
# Copy this file to .env and fill in your actual values
# cp .env.example .env

# ============================================
# Application Settings
# ============================================
APP_NAME=AI Character Chat System
DEBUG=false
ENVIRONMENT=development  # development, staging, production
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# ============================================
# Server Settings
# ============================================
HOST=0.0.0.0
PORT=8000

# ============================================
# Database Settings
# ============================================
# PostgreSQL connection string
# Format: postgresql+asyncpg://user:password@host:port/database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/ai_chat_system

# Connection pool settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30

# ============================================
# LLM Provider Settings
# ============================================
# Default LLM provider (openai, anthropic, google, ollama)
DEFAULT_LLM_PROVIDER=openai

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-sonnet-20240229
ANTHROPIC_TEMPERATURE=0.7
ANTHROPIC_MAX_TOKENS=2000

# Google (Gemini)
GOOGLE_API_KEY=...
GOOGLE_MODEL=gemini-pro
GOOGLE_TEMPERATURE=0.7
GOOGLE_MAX_TOKENS=2000

# Ollama (Local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_TEMPERATURE=0.7

# ============================================
# Embedding Settings
# ============================================
EMBEDDING_PROVIDER=openai  # openai, ollama
EMBEDDING_MODEL=text-embedding-ada-002
EMBEDDING_DIMENSION=1536

# ============================================
# Memory System Settings
# ============================================
# Memory Evolution
MEMORY_DECAY_RATE=0.01
MEMORY_REINFORCEMENT_FACTOR=0.1
FORGETTING_CURVE_ENABLED=true

# Retrieval Score Weights (must sum to 1.0)
RETRIEVAL_ALPHA=0.3  # Recency weight
RETRIEVAL_BETA=0.4   # Memory Strength weight
RETRIEVAL_GAMMA=0.3  # Relevance weight

# Reflection Generation
REFLECTION_THRESHOLD=10.0  # Importance sum threshold
REFLECTION_MIN_OBSERVATIONS=5

# User Portrait
PORTRAIT_UPDATE_THRESHOLD=3  # New reflections needed
PORTRAIT_CONFIDENCE_DECAY=0.05

# ============================================
# Character Settings
# ============================================
CHARACTER_NAME=ENE
CHARACTER_PERSONA=A thoughtful AI companion who remembers and understands

# Initial emotion values (0.0 - 1.0)
CHARACTER_INITIAL_JOY=0.5
CHARACTER_INITIAL_SADNESS=0.5
CHARACTER_INITIAL_ANGER=0.5
CHARACTER_INITIAL_SURPRISE=0.5
CHARACTER_INITIAL_FEAR=0.5
CHARACTER_INITIAL_DISGUST=0.5

# ============================================
# Conversation Policy
# ============================================
MAX_CONSECUTIVE_QUESTIONS=3
MIN_RESPONSE_LENGTH=50
MAX_RESPONSE_LENGTH=500
CONVERSATION_MODE=casual  # casual, serious, playful

# ============================================
# WebSocket Settings
# ============================================
WS_HEARTBEAT_INTERVAL=30  # seconds
WS_MAX_CONNECTIONS=100
WS_MESSAGE_QUEUE_SIZE=1000

# ============================================
# CORS Settings
# ============================================
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

# ============================================
# Security Settings
# ============================================
# JWT Secret (generate with: openssl rand -hex 32)
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# API Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# ============================================
# Background Tasks
# ============================================
# Memory decay task (cron format: minute hour day month day_of_week)
MEMORY_DECAY_SCHEDULE=0 0 * * *  # Daily at midnight

# Portrait update task
PORTRAIT_UPDATE_SCHEDULE=0 */6 * * *  # Every 6 hours

# ============================================
# Monitoring & Logging
# ============================================
# Sentry (Error tracking)
SENTRY_DSN=
SENTRY_ENVIRONMENT=development

# Logging
LOG_FORMAT=json  # json, text
LOG_FILE_PATH=logs/app.log
LOG_ROTATION=1 day
LOG_RETENTION=30 days

# ============================================
# AWS Settings (for deployment)
# ============================================
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# S3 (for file storage, if needed)
S3_BUCKET_NAME=

# ============================================
# Redis (for caching, if needed)
# ============================================
REDIS_URL=redis://localhost:6379/0
REDIS_ENABLED=false

# ============================================
# Testing
# ============================================
TEST_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/ai_chat_system_test
TEST_OPENAI_API_KEY=sk-test-...
```

---

## 사용 방법

### 1. 개발 환경 설정

```bash
# .env.example 복사
cp .env.example .env

# .env 파일 편집
nano .env  # 또는 vim, code 등

# 필수 값 설정
# - DATABASE_URL
# - OPENAI_API_KEY (또는 다른 LLM Provider)
# - JWT_SECRET_KEY
```

### 2. 환경별 설정

**개발 환경** (`.env`):
```bash
DEBUG=true
ENVIRONMENT=development
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/ai_chat_dev
```

**프로덕션 환경** (`.env.production`):
```bash
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO
DATABASE_URL=postgresql+asyncpg://user:password@prod-db.example.com:5432/ai_chat_prod
```

### 3. Docker Compose 사용 시

```yaml
# docker-compose.yml
services:
  app:
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/ai_chat_system
```

---

## 보안 주의사항

1. **절대 커밋하지 말 것**:
   - `.env` 파일은 `.gitignore`에 추가
   - API 키, 비밀번호 등 민감 정보 포함

2. **프로덕션 환경**:
   - 강력한 JWT_SECRET_KEY 사용
   - DEBUG=false 설정
   - 실제 API 키 사용

3. **환경 변수 관리**:
   - AWS Secrets Manager
   - HashiCorp Vault
   - Docker Secrets

---

## .gitignore 추가

```gitignore
# .gitignore

# Environment variables
.env
.env.local
.env.*.local
.env.production

# Logs
logs/
*.log

# Database
*.db
*.sqlite

# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

---

## 환경 변수 검증

```python
# src/core/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Character Chat System"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str  # Required
    
    # LLM
    DEFAULT_LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    
    # Memory
    MEMORY_DECAY_RATE: float = 0.01
    RETRIEVAL_ALPHA: float = 0.3
    RETRIEVAL_BETA: float = 0.4
    RETRIEVAL_GAMMA: float = 0.3
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def validate_retrieval_weights(self):
        """Retrieval Score 가중치 합 검증"""
        total = self.RETRIEVAL_ALPHA + self.RETRIEVAL_BETA + self.RETRIEVAL_GAMMA
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Retrieval weights must sum to 1.0, got {total}")

settings = Settings()
settings.validate_retrieval_weights()
```

이제 환경 변수 설정이 완료되었습니다!