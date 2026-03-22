# Data Models

## Database Schema (PostgreSQL + pgvector)

### Person (사용자)
```sql
CREATE TABLE person (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    profile TEXT,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
);
```

### Message (원본 메시지)
```sql
CREATE TYPE action_type AS ENUM ('AI', 'PERSON');

CREATE TABLE message (
    id SERIAL PRIMARY KEY,
    person_id INTEGER REFERENCES person(id),
    content TEXT NOT NULL,
    action action_type NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    last_access_time TIMESTAMP DEFAULT NOW() NOT NULL,
    importance_score FLOAT DEFAULT 0.5,
    access_count INTEGER DEFAULT 0,
    embedding VECTOR(1536),
    metadata JSONB
);
```

### Observation (검색 친화적 사건 표현)
```sql
CREATE TABLE observation (
    id SERIAL PRIMARY KEY,
    person_id INTEGER REFERENCES person(id),
    message_id INTEGER REFERENCES message(id),
    content TEXT NOT NULL,
    importance_score FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    last_access_time TIMESTAMP DEFAULT NOW() NOT NULL,
    access_count INTEGER DEFAULT 0,
    embedding VECTOR(1536),
    metadata JSONB
);
```

### Episode (사건 묶음)
```sql
CREATE TYPE episode_status AS ENUM ('ONGOING', 'COMPLETED');

CREATE TABLE episode (
    id SERIAL PRIMARY KEY,
    person_id INTEGER REFERENCES person(id),
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    purpose TEXT,
    turning_point TEXT,
    conclusion TEXT,
    importance FLOAT DEFAULT 1.0 NOT NULL,
    status episode_status DEFAULT 'ONGOING',
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL,
    access_count INTEGER DEFAULT 0,
    embedding VECTOR(1536),
    metadata JSONB
);

CREATE TABLE episode_message (
    id SERIAL PRIMARY KEY,
    episode_id INTEGER REFERENCES episode(id),
    message_id INTEGER REFERENCES message(id),
    sequence_order INTEGER NOT NULL
);
```

### Reflection (상위 의미 추론)
```sql
CREATE TABLE reflection (
    id SERIAL PRIMARY KEY,
    person_id INTEGER REFERENCES person(id),
    parent_id INTEGER REFERENCES reflection(id),
    content TEXT NOT NULL,
    importance_score FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    last_access_time TIMESTAMP DEFAULT NOW() NOT NULL,
    access_count INTEGER DEFAULT 0,
    embedding VECTOR(1536),
    metadata JSONB
);

CREATE TABLE reflection_source (
    id SERIAL PRIMARY KEY,
    reflection_id INTEGER REFERENCES reflection(id),
    source_type TEXT NOT NULL,  -- 'message', 'observation', 'episode'
    source_id INTEGER NOT NULL
);
```

### Tag (키워드 인덱싱)
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

### Emotion Record (감정 이력)
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

### Interest (사용자 관심사)
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

### Dialogue Plan (대화 계획)
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

### User Portrait (사용자 프로필)
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

### Memory Access History (기억 접근 이력)
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
