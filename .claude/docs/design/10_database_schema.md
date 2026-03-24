# Database Schema (Full DDL)

PostgreSQL + pgvector 기반 전체 스키마입니다. `04_data_models.md`의 초기 설계보다 발전된 최신 버전입니다.

사용자 이해 테이블 + ERD: [10_database_schema_user.md](10_database_schema_user.md)

## 주요 설계 결정

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| UUID vs SERIAL | `participant`, `message`는 UUID / 나머지는 SERIAL | 외부 노출 최소화, INTEGER JOIN 성능 |
| `memory_base` 패턴 | 모든 기억 객체의 공통 속성 통합 | Memory Evolution 통합 관리, 벡터 검색 단일화 |
| `episode_message` 제거 | `message.episode_id` FK로 대체 | 중간 테이블 제거, 쿼리 단순화 |
| `disclosure_weight` | 삭제 대신 가중치로 기억 억제 | 데이터 보존 + 출현도 제어 |
| `user_portrait` 스냅샷 | `user_state_snapshot` + 매핑 테이블 | Portrait 재생성 시점 상태 추적 |

## DDL — 핵심 테이블 (대화자·감정·메모리)

```sql
-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================================
-- 1. 대화자 (Participants)
-- ============================================================

CREATE TYPE participant_type AS ENUM ('HUMAN', 'AI_CHARACTER');

CREATE TABLE participant (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type       participant_type NOT NULL,
    name       TEXT NOT NULL,
    profile    TEXT,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX participant_type_idx ON participant(type);

-- ============================================================
-- 2. AI 상태 및 감정 (Character State & Emotions)
-- ============================================================

-- emotion_history는 character_state보다 먼저 생성 (FK 순서)
CREATE TABLE emotion_history (
    id             SERIAL PRIMARY KEY,
    character_id   UUID REFERENCES participant(id) NOT NULL,
    message_id     UUID,  -- message 테이블 생성 후 FK 추가
    joy            FLOAT NOT NULL CHECK (joy BETWEEN 0 AND 1),
    sadness        FLOAT NOT NULL CHECK (sadness BETWEEN 0 AND 1),
    anger          FLOAT NOT NULL CHECK (anger BETWEEN 0 AND 1),
    surprise       FLOAT NOT NULL CHECK (surprise BETWEEN 0 AND 1),
    fear           FLOAT NOT NULL CHECK (fear BETWEEN 0 AND 1),
    disgust        FLOAT NOT NULL CHECK (disgust BETWEEN 0 AND 1),
    trigger_reason TEXT,
    created_at     TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX emotion_history_character_idx ON emotion_history(character_id, created_at DESC);
CREATE INDEX emotion_history_message_idx ON emotion_history(message_id);

CREATE TABLE character_state (
    id                SERIAL PRIMARY KEY,
    character_id      UUID REFERENCES participant(id) UNIQUE NOT NULL,
    latest_emotion_id INTEGER REFERENCES emotion_history(id),
    energy_level      FLOAT DEFAULT 0.5 NOT NULL CHECK (energy_level BETWEEN 0 AND 1),
    engagement_level  FLOAT DEFAULT 0.5 NOT NULL CHECK (engagement_level BETWEEN 0 AND 1),
    conversation_mode TEXT,  -- 'casual', 'serious', 'playful', etc.
    updated_at        TIMESTAMP DEFAULT NOW() NOT NULL
);

-- ============================================================
-- 3. 기억 시스템 (Memory System)
-- ============================================================

CREATE TABLE memory_base (
    id                 SERIAL PRIMARY KEY,
    owner_id           UUID REFERENCES participant(id) NOT NULL,
    memory_type        TEXT NOT NULL,  -- 'message', 'observation', 'episode', 'reflection'
    importance_score   FLOAT NOT NULL CHECK (importance_score BETWEEN 0 AND 1),
    memory_strength    FLOAT NOT NULL CHECK (memory_strength BETWEEN 0 AND 1),
    access_count       INTEGER DEFAULT 0 NOT NULL,
    -- Memory Suppression: 삭제 대신 disclosure_weight 낮춰 억제
    -- Retrieval Score = base_score * disclosure_weight
    disclosure_weight  FLOAT DEFAULT 1.0 NOT NULL CHECK (disclosure_weight BETWEEN 0 AND 1),
    suppressed         BOOLEAN DEFAULT FALSE NOT NULL,
    suppression_reason TEXT,  -- 'user_request' | 'sensitivity_high' | 'system'
    created_at         TIMESTAMP DEFAULT NOW() NOT NULL,
    last_accessed_at   TIMESTAMP DEFAULT NOW() NOT NULL,
    embedding          VECTOR(1536),  -- OpenAI ada-002
    metadata           JSONB
);

CREATE INDEX memory_base_owner_idx ON memory_base(owner_id, created_at DESC);
CREATE INDEX memory_base_type_idx ON memory_base(memory_type);
CREATE INDEX memory_base_strength_idx ON memory_base(memory_strength DESC);
CREATE INDEX memory_base_owner_strength_idx ON memory_base(owner_id, memory_strength DESC);

-- 벡터 검색 인덱스 (HNSW)
CREATE INDEX memory_base_embedding_idx ON memory_base
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- episode는 message보다 먼저 생성 (message.episode_id FK 순서)
CREATE TYPE episode_status AS ENUM ('ONGOING', 'COMPLETED');

CREATE TABLE episode (
    id                    SERIAL PRIMARY KEY,
    memory_id             INTEGER REFERENCES memory_base(id) UNIQUE NOT NULL,
    title                 TEXT NOT NULL,
    summary               TEXT NOT NULL,
    purpose               TEXT,
    turning_point         TEXT,
    conclusion            TEXT,
    status                episode_status DEFAULT 'ONGOING' NOT NULL,
    avg_emotional_valence FLOAT CHECK (avg_emotional_valence BETWEEN -1 AND 1),
    avg_emotional_arousal FLOAT CHECK (avg_emotional_arousal BETWEEN 0 AND 1),
    created_at            TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at            TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX episode_memory_idx ON episode(memory_id);
CREATE INDEX episode_status_idx ON episode(status);
CREATE INDEX episode_valence_idx ON episode(avg_emotional_valence);

CREATE TABLE message (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id  INTEGER REFERENCES memory_base(id) UNIQUE NOT NULL,
    episode_id INTEGER REFERENCES episode(id),  -- episode_message 테이블 대체
    sender_id  UUID REFERENCES participant(id) NOT NULL,
    content    TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX message_sender_idx ON message(sender_id, created_at DESC);
CREATE INDEX message_memory_idx ON message(memory_id);
CREATE INDEX message_episode_idx ON message(episode_id, created_at);

-- emotion_history.message_id FK 추가 (message 생성 후)
ALTER TABLE emotion_history
    ADD CONSTRAINT emotion_history_message_fk
    FOREIGN KEY (message_id) REFERENCES message(id);

CREATE TABLE observation (
    id                    SERIAL PRIMARY KEY,
    memory_id             INTEGER REFERENCES memory_base(id) NOT NULL,
    content               TEXT NOT NULL,
    -- 감정 스냅샷 요약 지표 (쿼리/인덱스용)
    emotional_valence     FLOAT CHECK (emotional_valence BETWEEN -1 AND 1),
    emotional_arousal     FLOAT CHECK (emotional_arousal BETWEEN 0 AND 1),
    emotional_alignment   FLOAT CHECK (emotional_alignment BETWEEN 0 AND 1),
    -- 상세 수치 (분석용)
    user_emotion_snapshot JSONB,  -- {"joy": 0.7, "sadness": 0.1, ...}
    ai_emotion_snapshot   JSONB,
    created_at            TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX observation_memory_idx ON observation(memory_id);
CREATE INDEX observation_valence_idx ON observation(emotional_valence);

CREATE TABLE reflection (
    id                   SERIAL PRIMARY KEY,
    memory_id            INTEGER REFERENCES memory_base(id) UNIQUE NOT NULL,
    parent_reflection_id INTEGER REFERENCES reflection(id),
    content              TEXT NOT NULL,
    created_at           TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX reflection_memory_idx ON reflection(memory_id);
CREATE INDEX reflection_parent_idx ON reflection(parent_reflection_id);

CREATE TABLE reflection_source (
    reflection_id    INTEGER REFERENCES reflection(id) ON DELETE CASCADE,
    source_memory_id INTEGER REFERENCES memory_base(id) ON DELETE CASCADE,
    PRIMARY KEY (reflection_id, source_memory_id)
);

CREATE INDEX reflection_source_reflection_idx ON reflection_source(reflection_id);
CREATE INDEX reflection_source_memory_idx ON reflection_source(source_memory_id);

CREATE TABLE memory_access_log (
    id                    SERIAL PRIMARY KEY,
    memory_id             INTEGER REFERENCES memory_base(id) ON DELETE CASCADE NOT NULL,
    accessed_at           TIMESTAMP DEFAULT NOW() NOT NULL,
    access_context        TEXT,
    retrieval_score       FLOAT,
    reinforcement_applied BOOLEAN DEFAULT FALSE NOT NULL
);

CREATE INDEX memory_access_log_memory_idx ON memory_access_log(memory_id, accessed_at DESC);
```
