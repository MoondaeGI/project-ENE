# Workflow Layer (LangGraph)

## 대화 흐름

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

workflow.add_node("autonomous_behavior", autonomous_behavior_node)
workflow.add_node("memory_retrieval", memory_retrieval_node)
workflow.add_node("emotion_analysis", emotion_subgraph)   # 서브그래프
workflow.add_node("dialogue_planning", dialogue_planning_node)
workflow.add_node("message_generation", message_generation_node)
workflow.add_node("memory_save", memory_save_subgraph)    # 서브그래프

workflow.set_entry_point("autonomous_behavior")
workflow.add_conditional_edges("autonomous_behavior", should_respond_router)
workflow.add_edge("memory_retrieval", "emotion_analysis")
workflow.add_edge("emotion_analysis", "dialogue_planning")
workflow.add_edge("dialogue_planning", "message_generation")
workflow.add_edge("message_generation", "memory_save")
workflow.add_edge("memory_save", END)

app = workflow.compile()
```

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
        workflow.add_node("analyze_user_emotion", ...)
        workflow.add_node("update_ai_emotion", ...)
        workflow.add_node("save_history", ...)
        workflow.add_node("check_extreme_emotion", ...)
        workflow.add_node("handle_extreme_emotion", ...)

        workflow.set_entry_point("analyze_user_emotion")
        workflow.add_edge("analyze_user_emotion", "update_ai_emotion")
        workflow.add_edge("update_ai_emotion", "save_history")
        workflow.add_edge("save_history", "check_extreme_emotion")
        workflow.add_conditional_edges(
            "check_extreme_emotion",
            self.should_handle_extreme,
            {"handle": "handle_extreme_emotion", "continue": END}
        )

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
        # 노드 순서:
        # save_message → create_observation → calculate_importance
        # → check_reflection_trigger
        #     → (임계값 도달) generate_reflection → update_user_portrait → END
        #     → (미도달) END

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