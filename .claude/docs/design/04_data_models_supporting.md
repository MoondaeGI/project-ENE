# Data Models — 보조 테이블

[← 04_data_models.md](04_data_models.md) 에서 이어지는 문서입니다.

## Tag (키워드 인덱싱)

```sql
CREATE TABLE tag (
    id SERIAL PRIMARY KEY,
    tag TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tag_message (
    tag_id INTEGER REFERENCES tag(id),
    message_id INTEGER REFERENCES message(id),
    UNIQUE(tag_id, message_id)
);
CREATE TABLE tag_observation (
    tag_id INTEGER REFERENCES tag(id),
    observation_id INTEGER REFERENCES observation(id),
    UNIQUE(tag_id, observation_id)
);
CREATE TABLE tag_reflection (
    tag_id INTEGER REFERENCES tag(id),
    reflection_id INTEGER REFERENCES reflection(id),
    UNIQUE(tag_id, reflection_id)
);
CREATE TABLE tag_episode (
    tag_id INTEGER REFERENCES tag(id),
    episode_id INTEGER REFERENCES episode(id),
    UNIQUE(tag_id, episode_id)
);
```

## Emotion Record (감정 이력)

```sql
CREATE TABLE emotion_record (
    id SERIAL PRIMARY KEY,
    person_id INTEGER REFERENCES person(id),
    message_id INTEGER REFERENCES message(id),
    joy FLOAT NOT NULL,
    sadness FLOAT NOT NULL,
    anger FLOAT NOT NULL,
    surprise FLOAT NOT NULL,
    fear FLOAT NOT NULL,
    disgust FLOAT NOT NULL,
    source TEXT NOT NULL,  -- 'user' or 'character'
    created_at TIMESTAMP DEFAULT NOW() NOT NULL
);
```

## Interest (사용자 관심사)

```sql
CREATE TABLE interest (
    id SERIAL PRIMARY KEY,
    person_id INTEGER REFERENCES person(id),
    topic TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    first_mentioned TIMESTAMP NOT NULL,
    last_mentioned TIMESTAMP NOT NULL,
    frequency INTEGER DEFAULT 1,
    metadata JSONB
);
```

## Dialogue Plan (대화 계획)

```sql
CREATE TABLE dialogue_plan (
    id SERIAL PRIMARY KEY,
    person_id INTEGER REFERENCES person(id),
    current_goal TEXT NOT NULL,
    sub_goals JSONB,
    response_intention TEXT NOT NULL,
    expected_outcome TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
);
```

## User Portrait (사용자 프로필)

```sql
CREATE TABLE user_portrait (
    id SERIAL PRIMARY KEY,
    person_id INTEGER REFERENCES person(id) UNIQUE,
    personality_traits JSONB NOT NULL,
    communication_style TEXT,
    interests JSONB,
    preferences JSONB,
    confidence_score FLOAT DEFAULT 0.5,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    last_updated TIMESTAMP DEFAULT NOW() NOT NULL,
    metadata JSONB
);
```

## Memory Access History (기억 접근 이력)

```sql
CREATE TABLE memory_access_history (
    id SERIAL PRIMARY KEY,
    memory_type TEXT NOT NULL,  -- 'message', 'observation', 'reflection', 'episode'
    memory_id INTEGER NOT NULL,
    accessed_at TIMESTAMP DEFAULT NOW() NOT NULL,
    access_context TEXT,
    reinforcement_applied BOOLEAN DEFAULT FALSE
);

CREATE INDEX memory_access_history_idx ON memory_access_history(memory_type, memory_id);
```

## 벡터 인덱스 (pgvector HNSW)

```sql
CREATE INDEX message_embedding_idx ON message
    USING hnsw (embedding vector_cosine_ops);

CREATE INDEX observation_embedding_idx ON observation
    USING hnsw (embedding vector_cosine_ops);

CREATE INDEX episode_embedding_idx ON episode
    USING hnsw (embedding vector_cosine_ops);

CREATE INDEX reflection_embedding_idx ON reflection
    USING hnsw (embedding vector_cosine_ops);
```
