# Agents

> 참고: #[[file:.kiro/specs/ai-character-chat-system/references/conversation_policy_research.md]]
> 참고: #[[file:.kiro/specs/ai-character-chat-system/references/ene.md]]

## 에이전트 목록

| 에이전트 | 역할 |
|---------|------|
| Dialogue Agent | 대화 생성 및 응답 관리 |
| Emotion Agent | 감정 분석 및 감정 상태 관리 |
| Planning Agent | 대화 목표 설정 및 응답 전략 계획 |
| Retrieval Agent | 관련 기억 검색 및 컨텍스트 구성 |
| Topic Recommender | 사용자 관심사 분석 및 주제 추천 |
| User Portrait Manager | 사용자 프로필 생성 및 업데이트 |
| Memory Evolution Engine | 기억 강도 관리 및 망각 곡선 적용 |

---

## 1. Dialogue Agent

대화 생성 및 응답을 관리합니다. User Portrait를 활용하여 개인화된 응답을 생성하며, `ConversationPolicy`의 `formality_deviation_threshold`를 참조하여 감정 강도에 따른 Formality Shift를 적용합니다.

**주요 책임**:
- Planning Agent의 `DialoguePlan`을 기반으로 최종 응답 생성
- User Portrait를 프롬프트에 통합하여 개인화
- Formality Shift: 감정 강도가 임계값 이상이면 캐릭터 기본 formality에서 일시적 이탈 허용
- Short Reaction 포함 여부는 `DialoguePlan.include_short_reaction`에 따름

```python
class DialogueAgent:
    def __init__(self, policy: ConversationPolicy):
        self.policy = policy

    async def generate_response(
        self,
        state: ConversationState,
        dialogue_plan: DialoguePlan,
        persona: CharacterPersona
    ) -> str

    async def apply_formality_shift(
        self,
        response: str,
        emotion_intensity: float,
        base_formality: str
    ) -> str
```

**응답 생성 프로세스**:
```python
async def generate_response(self, state, dialogue_plan, persona) -> str:
    user_portrait = await self.portrait_manager.get_portrait(state.user_id)

    context = self.build_context_with_portrait(
        state.retrieved_memories,
        user_portrait,
        dialogue_plan,
        persona
    )

    response = await self.llm_adapter.generate(context)

    # Formality Shift: 감정 강도 임계값 초과 시에만 적용
    emotion_intensity = state.emotion_state.intensity()
    if emotion_intensity >= self.policy.formality_deviation_threshold:
        response = await self.apply_formality_shift(
            response, emotion_intensity, persona.base_formality
        )

    return response
```

**CharacterPersona 구조**:
```python
@dataclass
class CharacterPersona:
    name: str
    personality: str        # 성격 설명
    speaking_style: str     # 말투
    base_formality: str     # 기본 격식 수준 (system prompt에서 고정)
    background: str         # 배경 스토리
    behavior_patterns: List[str]
    system_prompt: str      # LLM에 전달될 시스템 프롬프트
```

---

## 2. Emotion Agent

사용자와 AI 캐릭터 양쪽의 감정을 추적하며, 감정 불일치(mismatch) 감지 시 Planning Agent에 repair 트리거 신호를 전달합니다.

**주요 책임**:
- 사용자 감정 분석 (다차원 감정 수치)
- AI 캐릭터 감정 업데이트
- 감정 이력 저장
- Repair 트리거 감지: 이전 응답의 감정 톤과 사용자 반응 간 불일치가 `repair_trigger_emotion_delta` 이상이면 `repair_needed` 플래그 설정

```python
class EmotionAgent:
    async def analyze_user_emotion(self, message: str) -> EmotionState
    async def update_character_emotion(
        self,
        current_emotion: EmotionState,
        context: ConversationState
    ) -> EmotionState
    async def detect_repair_trigger(
        self,
        prev_ai_emotion: EmotionState,
        current_user_emotion: EmotionState,
        delta_threshold: float
    ) -> bool
    async def get_emotion_history(self, user_id: str, limit: int) -> List[EmotionRecord]
```

**EmotionState 구조**:
```python
@dataclass
class EmotionState:
    joy: float      # 0.0 ~ 1.0
    sadness: float
    anger: float
    surprise: float
    fear: float
    disgust: float
    timestamp: datetime

    def dominant_emotion(self) -> str:
        emotions = {'joy': self.joy, 'sadness': self.sadness, 'anger': self.anger,
                    'surprise': self.surprise, 'fear': self.fear, 'disgust': self.disgust}
        return max(emotions, key=emotions.get)

    def intensity(self) -> float:
        """지배 감정의 강도 (Formality Shift 임계값 비교에 사용)"""
        return max(self.joy, self.sadness, self.anger,
                   self.surprise, self.fear, self.disgust)
```

---

## 3. Planning Agent

`ConversationPolicy` 설정 객체를 주입받아 모든 정책 규칙을 내부에서 적용하며, Emotion Agent로부터 repair 트리거 신호를 받아 응답 모드를 결정합니다.

**주요 책임**:
- 현재 대화 목표 설정 및 `DialogueIntention` 생성
- `ConversationPolicy` 규칙 적용 (연속 질문 제한, Short Reaction 조건 등)
- Clarification Decision: 모호성 점수 계산 후 명확화 요청 여부 결정
- Anti-Sycophancy: 잘못된 전제(Loaded Premise) 감지 시 정중한 수정 전략 선택
- Repair Mode 결정: `repair_needed` 플래그 수신 시 repair 응답 전략 활성화
- Common Ground State 참조 및 `assumed_referents` 활용

```python
class PlanningAgent:
    def __init__(self, policy: ConversationPolicy):
        self.policy = policy

    async def plan(
        self,
        state: ConversationState,
        common_ground: CommonGroundState,
        repair_needed: bool = False
    ) -> DialoguePlan

    async def decide_clarification(
        self,
        message: str,
        common_ground: CommonGroundState
    ) -> ClarificationDecision

    async def check_sycophancy(
        self,
        user_message: str,
        proposed_response: str
    ) -> SycophancyCheckResult
```

**응답 전략 결정 흐름**:
```python
async def plan(self, state, common_ground, repair_needed=False) -> DialoguePlan:
    if repair_needed:
        return DialoguePlan(response_intention=ResponseIntention.REPAIR, ...)

    clarification = await self.decide_clarification(state.message, common_ground)
    sycophancy = await self.check_sycophancy(state.message, ...)
    ask_question = self._can_ask_question(state.conversation_history)
    include_short_reaction = self._has_strong_signal(state)

    return DialoguePlan(
        ask_question=ask_question,
        include_short_reaction=include_short_reaction,
        clarification_request=clarification.clarification_prompt,
        sycophancy_correction=sycophancy.correction_strategy,
        ...
    )
```

**관련 데이터 구조**:
```python
@dataclass
class ClarificationDecision:
    should_clarify: bool
    ambiguity_score: float   # 0.0 ~ 1.0
    clarification_prompt: Optional[str]

@dataclass
class SycophancyCheckResult:
    has_loaded_premise: bool
    loaded_premise: Optional[str]
    correction_strategy: Optional[str]  # "acknowledge_then_correct" 등

@dataclass
class CommonGroundState:
    shared_facts: List[str]
    assumed_referents: Dict[str, str]  # 대명사/지시어 → 실제 지시 대상
    open_questions: List[str]
    last_topic: Optional[str]
    turn_count: int
```

---

## 4. Retrieval Agent

Memory Evolution Engine과 통합되어 기억 강화 및 접근 이력을 관리하며, Memory Disclosure 필터와 Common Ground State 업데이트를 담당합니다.

**주요 책임**:
- Retrieval Score 기반 기억 검색 및 Top-K 선택
- Memory Disclosure 필터 적용 (`disclosure_weight` 임계값 미만 기억 제외)
- Common Ground State 업데이트 (`assumed_referents`, `shared_facts`)
- 접근 기록 및 Memory Strength 강화

```python
class RetrievalAgent:
    def __init__(
        self,
        memory_evolution_engine: MemoryEvolutionEngine,
        disclosure_threshold: float = 0.3
    ):
        self.memory_evolution = memory_evolution_engine
        self.disclosure_threshold = disclosure_threshold

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
    async def prioritize_memories(
        self,
        memories: List[Memory],
        current_goal: DialogueGoal
    ) -> List[Memory]
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

    memories = await self.filter_by_disclosure(memories)

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

사용자 관심사를 분석하고 주제를 추천합니다.

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

`ConversationPolicy`는 별도 에이전트나 노드가 아닌, **LangGraph 그래프 초기화 시 주입되는 불변 설정 객체**입니다.

**설계 원칙**:
- 별도 Policy Check Node 없음 → Planning Agent 내부 제약 조건으로 처리
- Formality는 캐릭터 system prompt에서 기본값 고정, 감정 강도가 임계값 초과 시에만 일시적 이탈 허용
- Short Reaction은 강한 signal(강한 동의, 놀람, 공감)이 있을 때만 조건부 포함

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

workflow = StateGraph(ConversationState)
workflow.add_node(
    "dialogue_planning",
    lambda state: dialogue_planning_node(state, policy=policy)
)
```

**정책 규칙 요약**:

| 정책 항목 | 규칙 | 담당 에이전트 |
|-----------|------|--------------|
| 연속 질문 제한 | 직전 응답이 질문이면 다음 응답에서 질문 금지 | Planning Agent |
| Short Reaction | `short_reaction_triggers` 조건 충족 시에만 포함 | Planning Agent |
| Clarification Decision | 모호성 점수 ≥ 임계값이고 세션 내 횟수 미초과 시 명확화 요청 | Planning Agent |
| Anti-Sycophancy | 잘못된 전제 감지 시 정중하게 수정 | Planning Agent |
| Repair Mode | 감정 불일치 감지 시 repair 응답 전략 선택 | Planning Agent |
| Formality Shift | 감정 강도 ≥ 임계값 시 캐릭터 기본 formality에서 일시적 이탈 허용 | Dialogue Agent |
