# Memory System

## Memory Stream 개요

```
원본 Message → Observation → Episode → Reflection → User Portrait
```

**Memory 공통 필드**:
```python
@dataclass
class Memory:
    id: int
    user_id: str
    content: str
    memory_type: MemoryType  # MESSAGE, OBSERVATION, EPISODE, REFLECTION
    importance_score: float  # 0.0 ~ 1.0 (LLM이 평가, 초기 Memory Strength로 사용)
    created_at: datetime
    last_access_time: datetime
    access_count: int
    embedding: Optional[List[float]]
    metadata: Dict[str, Any]
```

---

## Memory Stream 컴포넌트

### MemoryStream

```python
class MemoryStream:
    async def add_message(self, user_id: str, content: str, action: ActionType) -> Message
    async def create_observation(self, message: Message) -> Observation
    async def get_recent_memories(self, user_id: str, limit: int) -> List[Memory]
    async def update_access_time(self, memory_id: int) -> None
```

### Reflection Generator

원시 기억으로부터 상위 의미와 패턴을 추론합니다. "요약"이 아닌 "상위 의미 추론"임에 주의.

**생성 조건**:
- Importance Score의 누적 합이 임계값(예: 10.0)에 도달
- 또는 일정 시간(예: 24시간)이 경과

**Reflection 예시**:
- "사용자는 구조 설계를 선호한다"
- "사용자는 실무 적용 가능성을 중요하게 본다"
- "사용자는 아이디어가 떠오르면 즉시 로드맵/테이블 설계까지 연결하려는 편이다"

```python
class ReflectionGenerator:
    async def should_generate_reflection(self, user_id: str) -> bool
    async def generate_reflection(
        self,
        user_id: str,
        recent_memories: List[Memory]
    ) -> Reflection
    async def store_reflection(self, reflection: Reflection) -> int
```

### Episode Manager

```python
class EpisodeManager:
    async def create_episode(
        self,
        user_id: str,
        title: str,
        messages: List[Message],
        metadata: EpisodeMetadata
    ) -> Episode
    async def get_episode(self, episode_id: int) -> Episode
    async def update_episode_status(self, episode_id: int, status: EpisodeStatus) -> None

@dataclass
class EpisodeMetadata:
    purpose: str
    turning_point: Optional[str]
    conclusion: Optional[str]
    emotion_changes: List[EmotionChange]
    importance: float

@dataclass
class Episode:
    id: int
    user_id: str
    title: str
    summary: str
    message_ids: List[int]
    metadata: EpisodeMetadata
    status: EpisodeStatus  # ONGOING, COMPLETED
    created_at: datetime
    updated_at: datetime
```

---

## Retrieval Engine

```python
class RetrievalEngine:
    async def retrieve(
        self,
        user_id: str,
        query: str,
        top_k: int = 10,
        weights: RetrievalWeights = None
    ) -> List[Memory]

@dataclass
class RetrievalWeights:
    recency: float = 0.3
    importance: float = 0.3   # Memory_Strength 사용
    relevance: float = 0.4

def calculate_retrieval_score(memory, query_embedding, current_time, weights):
    # Recency: exponential decay
    hours_since_access = (current_time - memory.last_access_time).total_seconds() / 3600
    recency_score = math.exp(-0.01 * hours_since_access)

    # Importance → Memory Strength 사용
    memory_strength = calculate_memory_strength(memory, current_time)

    # Relevance: cosine similarity
    relevance_score = cosine_similarity(memory.embedding, query_embedding)

    return (weights.recency * recency_score +
            weights.importance * memory_strength +
            weights.relevance * relevance_score)
```

---

## Memory Evolution Engine

```python
class MemoryEvolutionEngine:
    async def calculate_memory_strength(self, memory: Memory, current_time: datetime) -> float
    async def apply_forgetting_curve(self, memory: Memory, decay_rate: float = 0.01) -> float
    async def reinforce_memory(self, memory_id: int, reinforcement_factor: float = 0.1) -> None
    async def decay_unused_memories(self, user_id: str, threshold_days: int = 30) -> List[int]
    async def get_memory_access_history(self, memory_id: int) -> List[MemoryAccess]
```

**Memory Strength 계산 공식**:
```python
def calculate_memory_strength(memory, current_time, decay_rate=0.01):
    hours_since_creation = (current_time - memory.created_at).total_seconds() / 3600
    time_decay = math.exp(-decay_rate * hours_since_creation)
    access_reinforcement = min(0.5, memory.access_count * 0.05)
    memory_strength = memory.importance_score * time_decay + access_reinforcement
    return min(1.0, max(0.0, memory_strength))
```

---

## User Portrait Manager

```python
class UserPortraitManager:
    async def get_portrait(self, user_id: str) -> UserPortrait
    async def update_portrait(self, user_id: str, reflections: List[Reflection]) -> UserPortrait
    async def build_portrait_from_reflections(self, reflections: List[Reflection]) -> UserPortrait
    async def get_portrait_confidence(self, user_id: str) -> float

@dataclass
class UserPortrait:
    user_id: str
    personality_traits: List[str]   # ["구조 설계 선호", "실무 지향적"]
    communication_style: str        # "직접적이고 기술적"
    interests: List[Interest]
    preferences: Dict[str, Any]     # {"response_style": "코드 예시 포함"}
    confidence_score: float         # 0.0 ~ 1.0
    created_at: datetime
    last_updated: datetime
    metadata: Dict[str, Any]
```

**Portrait 생성 프로세스**:
1. 모든 Reflection 수집
2. 카테고리별 분류 (personality, communication, interests)
3. LLM으로 통합 프로필 생성
4. 신뢰도 계산 (Reflection 개수와 일관성 기반)

---

## Memory Disclosure 필터

Retrieval Agent가 검색된 기억을 응답 컨텍스트에 포함하기 전 `disclosure_weight` 확인:

```python
async def filter_by_disclosure(memories: List[Memory]) -> List[Memory]:
    return [m for m in memories if m.disclosure_weight >= DISCLOSURE_THRESHOLD]
```

- `disclosure_weight < threshold`: 컨텍스트에서 제외 (기억 자체는 DB에 유지)
- Memory Suppression: 삭제 대신 `disclosure_weight`를 낮춰 자연스럽게 억제
- Retrieval Score 계산 시: `base_score * disclosure_weight` 적용
