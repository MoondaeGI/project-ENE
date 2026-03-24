# Data Models

> **주의**: 이 문서는 초기 설계안입니다. 최신 스키마는 [10_database_schema.md](10_database_schema.md)를 참조하세요.

보조 테이블 (Tag, Emotion, Interest, Portrait 등): [04_data_models_supporting.md](04_data_models_supporting.md)

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
