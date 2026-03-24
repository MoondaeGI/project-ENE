# Agents

## 에이전트 목록

| 에이전트 | 역할 |
| --- | --- |
| Dialogue Agent | 대화 생성 및 응답 관리 |
| Emotion Agent | 감정 분석 및 감정 상태 관리 |
| Planning Agent | 대화 목표 설정 및 응답 전략 계획 |
| Retrieval Agent | 관련 기억 검색 및 컨텍스트 구성 |
| Topic Recommender | 사용자 관심사 분석 및 주제 추천 |
| User Portrait Manager | 사용자 프로필 생성 및 업데이트 |
| Memory Evolution Engine | 기억 강도 관리 및 망각 곡선 적용 |

에이전트 상세 설계: [02_agents_detail.md](02_agents_detail.md)

---

## 1. Dialogue Agent

User Portrait를 활용하여 개인화된 응답을 생성하며, `ConversationPolicy.formality_deviation_threshold`를 참조하여 감정 강도에 따른 Formality Shift를 적용합니다.

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
        state.retrieved_memories, user_portrait, dialogue_plan, persona
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
    personality: str
    speaking_style: str
    base_formality: str     # 기본 격식 수준 (system prompt에서 고정)
    background: str
    behavior_patterns: List[str]
    system_prompt: str      # LLM에 전달될 시스템 프롬프트
```

---

## 2. Emotion Agent

사용자와 AI 캐릭터 양쪽의 감정을 추적하며, 감정 불일치(mismatch) 감지 시 Planning Agent에 repair 트리거 신호를 전달합니다.

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
        """지배 감정의 강도 — Formality Shift 임계값 비교에 사용"""
        return max(self.joy, self.sadness, self.anger,
                   self.surprise, self.fear, self.disgust)
```

---

## 3. Planning Agent

`ConversationPolicy` 설정 객체를 주입받아 모든 정책 규칙을 내부에서 적용하며, Emotion Agent로부터 repair 트리거 신호를 받아 응답 모드를 결정합니다.

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
