# Agents Detail: Retrieval, Topic, ConversationPolicy

[← 02_agents.md](02_agents.md) 에서 이어지는 문서입니다.

---

## 4. Retrieval Agent

Memory Evolution Engine과 통합되어 기억 강화 및 접근 이력을 관리하며, Memory Disclosure 필터와 Common Ground State 업데이트를 담당합니다.

```python
class RetrievalAgent:
    def __init__(
        self,
        memory_evolution_engine: MemoryEvolutionEngine,
        disclosure_threshold: float = 0.3
    ):
        ...

    async def retrieve_relevant_memories(
        self,
        user_id: str,
        query: str,
        retrieval_config: RetrievalConfig
    ) -> List[Memory]

    async def filter_by_disclosure(self, memories: List[Memory]) -> List[Memory]
    async def update_common_ground(
        self,
        state: ConversationState,
        retrieved_memories: List[Memory]
    ) -> CommonGroundState
    async def build_context(self, memories: List[Memory], max_tokens: int) -> str
```

**검색 프로세스**:

```python
async def retrieve_relevant_memories(self, user_id, query, retrieval_config) -> List[Memory]:
    memories = await self.search_memories(user_id, query, retrieval_config)

    current_time = datetime.now()
    for memory in memories:
        memory.strength = await self.memory_evolution.calculate_memory_strength(
            memory, current_time
        )

    memories = await self.filter_by_disclosure(memories)  # disclosure_weight 필터

    for memory in memories[:retrieval_config.top_k]:
        await self.memory_evolution.reinforce_memory(memory.id)
        await self.record_access(memory)

    return memories[:retrieval_config.top_k]
```

**RetrievalConfig 구조**:

```python
@dataclass
class RetrievalConfig:
    top_k: int = 10
    weights: RetrievalWeights = field(default_factory=RetrievalWeights)
    memory_types: List[MemoryType] = field(
        default_factory=lambda: [
            MemoryType.REFLECTION,
            MemoryType.OBSERVATION,
            MemoryType.MESSAGE
        ]
    )
    time_range: Optional[timedelta] = None
```

---

## 5. Topic Recommender

```python
class TopicRecommender:
    async def extract_interests(
        self,
        user_id: str,
        recent_conversations: List[Message]
    ) -> List[Interest]

    async def recommend_topics(
        self,
        user_id: str,
        current_context: ConversationState
    ) -> List[Topic]

    async def update_interest_profile(
        self,
        user_id: str,
        user_reaction: UserReaction
    ) -> None
```

**데이터 구조**:

```python
@dataclass
class Interest:
    topic: str
    confidence: float       # 0.0 ~ 1.0
    first_mentioned: datetime
    last_mentioned: datetime
    frequency: int

@dataclass
class Topic:
    title: str
    description: str
    relevance_score: float
    source: TopicSource     # USER_HISTORY, EXTERNAL_TREND, RELATED_INTEREST
    suggested_timing: str   # "대화 시작 시", "주제 전환 시"
```

---

## 6. ConversationPolicy (설정 객체)

별도 에이전트나 노드가 아닌, **LangGraph 그래프 초기화 시 주입되는 불변 설정 객체**입니다.

```python
@dataclass(frozen=True)
class ConversationPolicy:
    # 질문 제한
    max_consecutive_questions: int = 1
    question_cooldown_turns: int = 2

    # Short Reaction 조건
    short_reaction_triggers: List[str] = field(
        default_factory=lambda: ["strong_agreement", "surprise", "empathy"]
    )

    # Clarification Decision
    clarification_threshold: float = 0.4
    max_clarification_per_session: int = 2

    # Anti-Sycophancy
    sycophancy_check_enabled: bool = True
    loaded_premise_detection: bool = True

    # Repair Policy
    repair_trigger_emotion_delta: float = 0.3
    repair_max_attempts: int = 2

    # Formality
    formality_deviation_threshold: float = 0.7
```

**주입 방식**:

```python
policy = ConversationPolicy()
workflow.add_node(
    "dialogue_planning",
    lambda state: dialogue_planning_node(state, policy=policy)
)
```

**정책 규칙 요약**:

| 정책 항목 | 규칙 | 담당 |
| --- | --- | --- |
| 연속 질문 제한 | 직전 응답이 질문이면 다음 응답에서 질문 금지 | Planning Agent |
| Short Reaction | `short_reaction_triggers` 조건 충족 시에만 포함 | Planning Agent |
| Clarification Decision | ambiguity_score ≥ 임계값 시 명확화 요청 | Planning Agent |
| Anti-Sycophancy | 잘못된 전제 감지 시 정중하게 수정 | Planning Agent |
| Repair Mode | 감정 불일치 감지 시 repair 응답 전략 선택 | Planning Agent |
| Formality Shift | 감정 강도 ≥ 임계값 시 기본 formality에서 일시적 이탈 | Dialogue Agent |
