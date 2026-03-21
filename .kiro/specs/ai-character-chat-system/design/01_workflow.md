# Workflow Layer (LangGraph)

## 대화 흐름 개요

```
사용자 메시지
    ↓
1. Autonomous Behavior Node  (응답 vs 침묵 결정)
    ↓ (조건부)
2. Memory Retrieval Node     (관련 기억 검색)
    ↓
3. Emotion Analysis Subgraph (감정 분석 - 복잡)
    ↓
4. Dialogue Planning Node    (대화 계획 + 정책 적용)
    ↓
5. Message Generation Node   (메시지 생성)
    ↓
6. Memory Save Subgraph      (메모리 저장 - 복잡)
    ↓
응답 반환
```

## Main Workflow (StateGraph)

```python
workflow = StateGraph(ConversationState)

# 노드 추가
workflow.add_node("autonomous_behavior", autonomous_behavior_node)
workflow.add_node("memory_retrieval", memory_retrieval_node)
workflow.add_node("emotion_analysis", emotion_subgraph)   # 서브그래프
workflow.add_node("dialogue_planning", dialogue_planning_node)
workflow.add_node("message_generation", message_generation_node)
workflow.add_node("memory_save", memory_save_subgraph)    # 서브그래프

# 흐름 정의
workflow.set_entry_point("autonomous_behavior")
workflow.add_conditional_edges("autonomous_behavior", should_respond_router)
workflow.add_edge("memory_retrieval", "emotion_analysis")
workflow.add_edge("emotion_analysis", "dialogue_planning")
workflow.add_edge("dialogue_planning", "message_generation")
workflow.add_edge("message_generation", "memory_save")
workflow.add_edge("memory_save", END)

app = workflow.compile()
```

**단순 노드** (순차적 처리):
- Autonomous Behavior: 응답할지 침묵할지 결정
- Memory Retrieval: 벡터 검색으로 관련 기억 가져오기
- Dialogue Planning: 대화 목표, 응답 의도 설정 및 ConversationPolicy 규칙 적용
- Message Generation: LLM으로 최종 응답 생성

**복잡한 노드** (서브그래프):
- Emotion Analysis Subgraph: 사용자/AI 감정 분석, 상태 업데이트, 이력 저장, 극단적 감정 처리
- Memory Save Subgraph: Message 저장, Observation 생성, Reflection 트리거, User Portrait 업데이트

## MainConversationChain 인터페이스

```python
class MainConversationChain:
    def __init__(
        self,
        autonomous_behavior: AutonomousBehaviorChain,
        memory_retrieval: MemoryRetrievalChain,
        emotion_orchestrator: EmotionOrchestrator,
        dialogue_planning: DialoguePlanningChain,
        message_generation: MessageGenerationChain,
        memory_save: MemorySaveOrchestrator
    )

    async def ainvoke(self, user_message: str, user_id: str) -> ConversationResult
    async def astream(self, user_message: str, user_id: str) -> AsyncIterator[str]
```

## Chain Components

### Autonomous Behavior Chain

AI 캐릭터의 자율적 행동을 결정합니다 (응답 vs 침묵).

```python
class AutonomousBehaviorChain:
    async def ainvoke(self, state: ChainState) -> BehaviorDecision

@dataclass
class BehaviorDecision:
    should_respond: bool
    action_type: str  # 'respond', 'silence', 'initiate'
    reason: str
```

### Memory Retrieval Chain

```python
class MemoryRetrievalChain:
    async def ainvoke(self, state: ChainState) -> List[Memory]

    async def retrieve(
        self,
        query: str,
        user_id: str,
        top_k: int = 10,
        alpha: float = 0.3,   # Recency weight
        beta: float = 0.4,    # Memory_Strength weight
        gamma: float = 0.3    # Relevance weight
    ) -> List[Memory]
```

### Dialogue Planning Chain

`ConversationPolicy` 설정 객체를 주입받아 모든 정책 규칙을 내부에서 처리합니다.

```python
class DialoguePlanningChain:
    def __init__(self, policy: ConversationPolicy):
        self.policy = policy

    async def ainvoke(self, state: ChainState) -> DialoguePlan

@dataclass
class DialoguePlan:
    current_goal: str
    response_intention: ResponseIntention  # EXPLAIN, COMFORT, GUIDE, ASSIST, REPAIR, CLARIFY
    expected_outcome: str
    sub_goals: List[str]
    include_short_reaction: bool
    ask_question: bool
    repair_mode: bool
    clarification_request: Optional[str]
    sycophancy_correction: Optional[str]
```

### Message Generation Chain

```python
class MessageGenerationChain:
    async def ainvoke(self, state: ChainState) -> str
    async def astream(self, state: ChainState) -> AsyncIterator[str]
```

## Subgraphs

### Emotion Analysis Subgraph

```python
class EmotionOrchestrator:
    def __init__(self):
        workflow = StateGraph(EmotionState)

        workflow.add_node("analyze_user_emotion", self.analyze_user)
        workflow.add_node("update_ai_emotion", self.update_ai)
        workflow.add_node("save_history", self.save_history)
        workflow.add_node("check_extreme_emotion", self.check_extreme)
        workflow.add_node("handle_extreme_emotion", self.handle_extreme)

        workflow.set_entry_point("analyze_user_emotion")
        workflow.add_edge("analyze_user_emotion", "update_ai_emotion")
        workflow.add_edge("update_ai_emotion", "save_history")
        workflow.add_edge("save_history", "check_extreme_emotion")
        workflow.add_conditional_edges(
            "check_extreme_emotion",
            self.should_handle_extreme,
            {"handle": "handle_extreme_emotion", "continue": END}
        )

        self.graph = workflow.compile()

    async def ainvoke(self, state: ChainState) -> EmotionState

@dataclass
class EmotionState:
    user_emotion: Dict[str, float]  # joy, sadness, anger, surprise, fear, disgust
    ai_emotion: Dict[str, float]
    trigger_reason: str
    is_extreme: bool
```

### Memory Save Subgraph

```python
class MemorySaveOrchestrator:
    def __init__(self):
        workflow = StateGraph(MemorySaveState)

        workflow.add_node("save_message", self.save_message)
        workflow.add_node("create_observation", self.create_observation)
        workflow.add_node("calculate_importance", self.calculate_importance)
        workflow.add_node("check_reflection_trigger", self.check_reflection)
        workflow.add_node("generate_reflection", self.generate_reflection)
        workflow.add_node("update_user_portrait", self.update_portrait)

        workflow.set_entry_point("save_message")
        workflow.add_edge("save_message", "create_observation")
        workflow.add_edge("create_observation", "calculate_importance")
        workflow.add_edge("calculate_importance", "check_reflection_trigger")
        workflow.add_conditional_edges(
            "check_reflection_trigger",
            self.should_generate_reflection,
            {"generate": "generate_reflection", "skip": END}
        )
        workflow.add_edge("generate_reflection", "update_user_portrait")
        workflow.add_edge("update_user_portrait", END)

        self.graph = workflow.compile()

    async def ainvoke(self, state: ChainState) -> MemorySaveResult

@dataclass
class MemorySaveState:
    message_id: str
    observation_id: str
    importance_score: float
    importance_sum: float
    reflection_threshold: float
    reflection_generated: bool
    portrait_updated: bool
```

## WebSocket Server

```python
class WebSocketServer:
    async def connect(self, websocket: WebSocket, user_id: str) -> None
    async def disconnect(self, user_id: str) -> None
    async def receive_message(self, user_id: str) -> Message
    async def send_message(self, user_id: str, message: str) -> None
    async def stream_response(self, user_id: str, chunks: AsyncIterator[str]) -> None
```
