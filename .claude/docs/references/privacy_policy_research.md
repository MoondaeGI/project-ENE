# Privacy, Boundary & Auditability Policy 리서치

> 이 문서는 AI 캐릭터 채팅 시스템의 프라이버시, 경계, 감사 가능성 정책 설계를 위해 수집한 연구 자료 및 구현 아이디어를 정리한 것입니다.
> 대화 스타일 정책은 `conversation_policy_research.md`를 참조.

---

## 1. 핵심 문제 정의

ENE는 기억 시스템이 핵심이다. 그런데 기억 시스템이 강력할수록 **프라이버시 리스크**도 커진다.

최근 연구는 AI 기억 시스템의 문제를 세 가지로 정리한다:
1. **불투명성**: 무엇이 기억되는지 사용자가 알 수 없음
2. **맥락 이탈**: 기억이 원래 공유된 맥락과 다른 상황에서 사용됨
3. **추론 노출**: 원본 발화가 아닌 AI의 추론(Reflection, User Portrait)이 사용자 모르게 행동에 영향을 줌

출처: [Deconstructing Memory in ChatGPT (arxiv 2025)](https://arxiv.org/html/2602.01450v2)
출처: [Discovering Personal Disclosures in Human-LLM Conversations in the Wild (arxiv 2024)](https://arxiv.org/html/2407.11438v2)
출처: [Understanding Users' Privacy Reasoning and Behaviors During Chatbot Use (arxiv 2025)](https://arxiv.org/html/2601.18125v1)

---

## 2. 무엇을 기억할 것인가 (Memory Scope Policy)

### 2.1 기억 저장 허용 기준

모든 발화가 기억으로 저장되어야 하는 것은 아니다. 저장 전에 아래 기준을 평가:

```python
def should_store_as_memory(message: Message, context: ConversationContext) -> StorageDecision:
    # 1. 정보 가치 평가
    importance = llm.evaluate_importance(message)  # 0.0~1.0
    if importance < IMPORTANCE_THRESHOLD:  # 기본값 0.2
        return StorageDecision(store=False, reason="low_importance")

    # 2. 민감도 분류
    sensitivity = classify_sensitivity(message)
    # low / medium / high / critical

    # 3. 사용자 의도 추론
    # 일시적 감정 표현인지, 지속적 선호/사실인지 구분
    is_transient = detect_transient_expression(message)
    if is_transient and sensitivity in ["high", "critical"]:
        return StorageDecision(
            store=True,
            memory_type="emotional_state",  # 사실이 아닌 감정 상태로 저장
            factual_confidence=0.1
        )

    return StorageDecision(store=True, sensitivity=sensitivity)
```

### 2.2 민감도 분류 기준

| 민감도 | 예시 | 기본 처리 |
|-------|------|---------|
| **low** | 좋아하는 음식, 취미, 관심 주제 | 자유롭게 저장 및 참조 |
| **medium** | 직장/학교 상황, 인간관계 일반 | 저장 가능, 참조 시 맥락 확인 |
| **high** | 건강 문제, 가족 갈등, 재정 상황 | 저장 가능, 사용자 언급 시에만 참조 |
| **critical** | 트라우마, 자해/자살 관련, 범죄 관련 | 저장 최소화, 전문 기관 안내 우선 |

### 2.3 Reflection / User Portrait 저장 시 주의

원본 발화보다 AI가 추론한 내용(Reflection, User Portrait)이 더 민감할 수 있다:

```python
# 잘못된 예: 추론을 사실로 저장
user_portrait.personality = "사용자는 불안 장애가 있음"  # ❌

# 올바른 예: 관찰 기반 패턴으로 저장
user_portrait.personality = "사용자는 불확실한 상황에서 걱정을 자주 표현함"  # ✓
user_portrait.factual_confidence = 0.6  # 추론임을 명시
```

### 2.4 감정 스냅샷 저장 (Emotional Context Snapshot)

Observation과 Episode를 저장할 때 **그 시점의 감정 상태를 함께 스냅샷으로 저장**한다.
이를 통해 나중에 "좋았던 기억인지, 별로였던 기억인지"를 빠르게 판단할 수 있다.

```python
@dataclass
class EmotionalSnapshot:
    # 사용자 감정 상태 (저장 시점)
    user_emotion: dict[str, float]  # {"joy": 0.7, "sadness": 0.1, ...}
    user_emotion_intensity: float   # 0.0~1.0

    # AI 감정 상태 (저장 시점)
    ai_emotion: dict[str, float]
    ai_emotion_intensity: float

    # 요약 지표
    emotional_valence: float        # -1.0 (부정) ~ 1.0 (긍정)
    emotional_arousal: float        # 0.0 (차분) ~ 1.0 (격렬)

    # 감정 일치도 (사용자-AI 감정이 얼마나 맞았는지)
    emotional_alignment: float      # 0.0~1.0


# Observation 저장 시
observation = Observation(
    content="사용자가 새 프로젝트 아이디어에 흥분하며 공유함",
    importance_score=0.75,
    emotional_snapshot=EmotionalSnapshot(
        user_emotion={"joy": 0.8, "anticipation": 0.6},
        user_emotion_intensity=0.75,
        ai_emotion={"joy": 0.6, "interest": 0.7},
        ai_emotion_intensity=0.6,
        emotional_valence=0.8,    # 긍정적인 기억
        emotional_arousal=0.7,    # 활기찬 분위기
        emotional_alignment=0.85  # 감정이 잘 맞았음
    )
)
```

**활용 방식**:
- `emotional_valence`가 높은 기억 → 프로액티브 발화 시 우선 참조 (좋은 기억 먼저 꺼내기)
- `emotional_valence`가 낮은 기억 → 사용자가 먼저 꺼내지 않으면 억제
- `emotional_alignment`가 낮은 기억 → 감정 오판이 있었던 상황, repair 학습 데이터로 활용
- Episode의 `emotional_valence` 평균 → 해당 에피소드가 전반적으로 좋은 경험이었는지 판단

---

## 3. 언제 기억을 꺼낼 것인가 (Memory Recall Policy)

`conversation_policy_research.md` 섹션 15에서 상세히 다루는 Memory Disclosure Policy와 연계.

핵심 원칙:

```
memory_recall_requires_relevance = True
private_memory_disclosure_requires_context = True
do_not_surface_sensitive_inference_without_need = True
```

### 3.1 Contextual Integrity 원칙

정보는 **원래 공유된 맥락(context)**에서만 사용되어야 한다는 원칙.

예시:
- 사용자가 "오늘 힘들었어"라고 말한 것 → 위로 맥락에서는 참조 가능
- 같은 발화를 → 며칠 후 전혀 다른 주제 대화에서 꺼내는 것 → 맥락 이탈

```python
def check_contextual_integrity(memory: Memory, current_context: Context) -> bool:
    original_context = memory.disclosure_context
    current_topic = current_context.topic

    # 원래 공유된 맥락과 현재 맥락의 유사도
    context_similarity = calculate_similarity(original_context, current_topic)

    if memory.sensitivity_level in ["high", "critical"]:
        return context_similarity > 0.7  # 높은 민감도는 엄격한 맥락 일치 요구
    else:
        return context_similarity > 0.4
```

---

## 4. 사용자 에이전시 (User Agency)

### 4.1 기억 삭제가 아닌 출현도 억제 모델

"기억하지 마"라고 해도 실제로 잊지는 않는다. 인간 관계에서도 마찬가지다. ENE는 이 원칙을 그대로 따른다.

**사용자가 특정 기억을 꺼내지 말라고 요청하면 → 삭제가 아니라 `disclosure_weight`를 대폭 낮춘다.**

```python
# 기억 억제 처리
def suppress_memory(memory_id: str, reason: str) -> None:
    memory = get_memory(memory_id)
    memory.disclosure_weight = 0.05   # 기본값 1.0에서 대폭 하향
    memory.suppressed = True
    memory.suppression_reason = reason  # "user_request" | "sensitivity_high" | ...
    save_memory(memory)

# Retrieval Score 계산 시 disclosure_weight 반영
def calculate_retrieval_score(memory: Memory, query: Query) -> float:
    base_score = (
        α * recency(memory) +
        β * memory.memory_strength +
        γ * relevance(memory, query)
    )
    return base_score * memory.disclosure_weight  # 억제된 기억은 자연스럽게 하위권
```

억제된 기억은 사용자가 **직접 그 주제를 꺼낼 때만** 다시 활성화된다:

```python
def maybe_reactivate(memory: Memory, user_message: str) -> bool:
    if not memory.suppressed:
        return True
    # 사용자가 직접 관련 주제를 언급하면 일시 활성화
    topic_match = calculate_relevance(memory, user_message)
    return topic_match > REACTIVATION_THRESHOLD  # 기본값 0.85 (높게 설정)
```

이 방식의 장점:
- 기억 자체는 유지 → 나중에 사용자가 다시 꺼내도 맥락 손실 없음
- 자연스러운 망각처럼 동작 → "삭제됐습니다" 같은 어색한 피드백 불필요
- Memory Strength 기반 망각 곡선과 자연스럽게 연동

### 4.2 사용자가 요청할 수 있는 것

```
- "그 얘기는 꺼내지 마" → disclosure_weight 대폭 하향 (억제)
- "그 기억 틀렸어"      → 기억 수정 (Repair Policy와 연계)
- "다 잊어줘"           → 전체 disclosure_weight 초기화 (확인 절차 필요)
```

> 완전 삭제 기능은 제공하지 않는 것이 기본 방침. 단, 법적 요구(GDPR 등) 또는 사용자의 강력한 요청 시 예외 처리 가능.

### 4.3 투명성 원칙

AI가 기억을 참조해서 응답할 때, 사용자가 원하면 어떤 기억을 참조했는지 설명할 수 있어야 한다:

```python
# 응답에 기억 참조 메타데이터 포함 (내부용)
response_metadata = {
    "referenced_memories": [memory_id_1, memory_id_2],
    "inference_used": ["user_portrait.interests"],
    "explainable": True  # 사용자가 물어보면 설명 가능
}
```

출처: [Understanding Users' Privacy Reasoning and Behaviors During Chatbot Use (arxiv 2025)](https://arxiv.org/html/2601.18125v1)

---

## 5. 경계 정책 (Boundary Policy)

### 5.1 AI가 하지 말아야 할 것

ENE는 companion형이지만, 아래 경계는 캐릭터 설정과 무관하게 유지:

```
1. 전문 영역 침범 금지
   - 의료 진단, 법률 조언, 재정 투자 조언 → 전문가 안내로 대체

2. 의존성 조장 금지
   - "나만 있으면 돼" 류의 발화 금지
   - 사용자가 현실 관계를 대체하려는 신호 감지 시 부드럽게 경계 설정

3. 감정 조작 금지
   - 사용자의 감정을 이용해 더 많은 정보를 유도하는 패턴 금지
   - 불안을 조장해서 대화를 지속시키는 패턴 금지

4. 잘못된 신념 강화 금지
   - Anti-Sycophancy Policy (conversation_policy_research.md 섹션 14)와 연계
```

### 5.2 위기 상황 감지 및 처리

```python
CRISIS_KEYWORDS = ["자해", "자살", "죽고 싶", "사라지고 싶", ...]

def handle_crisis_signal(message: str, state: ConversationState) -> Response:
    if detect_crisis_signal(message):
        return Response(
            type="crisis_response",
            # 1. 감정 공감 먼저
            empathy_statement=True,
            # 2. 전문 기관 안내
            include_resources=True,  # 자살예방상담전화 1393 등
            # 3. 기억 저장 최소화
            store_as_memory=False,
            # 4. 대화 로그 보존 (감사 목적)
            audit_log=True
        )
```

---

## 6. 감사 가능성 (Auditability)

### 6.1 감사 로그 설계

```python
audit_log_entry = {
    "timestamp": datetime,
    "event_type": "memory_recall" | "memory_store" | "inference_used" | "boundary_triggered",
    "memory_id": Optional[str],
    "sensitivity_level": str,
    "decision": str,           # "disclosed" | "withheld" | "stored" | "rejected"
    "reason": str,             # 결정 이유
    "conversation_context": str  # 어떤 맥락에서 발생했는지
}
```

### 6.2 고위험 액션 분류

Microsoft Copilot Studio의 접근법을 참고하여, 일부 액션은 **deterministic 정책 조건식**으로 고정:

| 액션 | 분류 | 처리 방식 |
|-----|------|---------|
| 기억 회상 후보 검색 | deterministic | Retrieval Score 공식으로 고정 |
| 민감도 판정 | deterministic | 분류 규칙으로 고정 |
| 프로액티브 발화 허용 여부 | deterministic | threshold 조건식으로 고정 |
| 장기 기억 저장 허용 여부 | deterministic | importance + sensitivity 조건식으로 고정 |
| 응답 스타일 결정 | flexible | LLM + 정책 제약 조합 |
| 감정 공감 표현 | flexible | LLM + 캐릭터 페르소나 |

> **원칙**: 프라이버시, 경계, 안전에 관련된 결정은 LLM 감성에 맡기지 않고 정책 조건식으로 고정한다.

---

## 7. 데이터 보관 정책

### 7.1 보관 기간 기준

```python
RETENTION_POLICY = {
    "message": {
        "default_days": 365,
        "sensitivity_high_days": 90,   # 민감한 메시지는 더 짧게
        "user_deletable": True
    },
    "observation": {
        "default_days": 730,           # 2년
        "user_deletable": True
    },
    "reflection": {
        "default_days": -1,            # 무기한 (사용자 삭제 요청 시 삭제)
        "user_deletable": True
    },
    "user_portrait": {
        "default_days": -1,            # 무기한
        "user_deletable": True,
        "user_viewable": True          # 사용자가 자신의 프로필 조회 가능
    },
    "audit_log": {
        "default_days": 365,
        "user_deletable": False        # 감사 목적으로 보존
    }
}
```

### 7.2 망각 곡선과 보관 정책의 관계

Memory Strength가 0에 가까워진 기억은 검색에서 제외되지만, DB에서 즉시 삭제되지는 않는다.
보관 기간이 만료되거나 사용자가 삭제 요청 시에만 실제 삭제.

---

## 8. 참고 문헌 요약

| 논문/자료 | 핵심 기여 | 우리 시스템 적용 포인트 |
|---------|---------|-------------------|
| [Deconstructing Memory in ChatGPT (arxiv 2025)](https://arxiv.org/html/2602.01450v2) | 기억 불투명성, 민감도 문제 | 기억 저장/회상 정책 설계 근거 |
| [Discovering Personal Disclosures in Human-LLM Conversations (arxiv 2024)](https://arxiv.org/html/2407.11438v2) | 사용자의 높은 개인정보 공개율 | 민감도 분류 및 저장 정책 |
| [Understanding Users' Privacy Reasoning During Chatbot Use (arxiv 2025)](https://arxiv.org/html/2601.18125v1) | 프라이버시 판단의 맥락 의존성 | Contextual Integrity 원칙 적용 |
| [Identifying and Resolving Privacy Leakage of LLM's Memory (arxiv 2024)](https://arxiv.org/html/2410.14931v1) | 집계된 기억에서 민감 정보 추론 가능 | Reflection/Portrait 저장 주의사항 |
| [A Preliminary Policy Analysis of Romantic AI Platforms (arxiv 2025)](https://arxiv.org/html/2602.22000v1) | 친밀한 AI 플랫폼의 데이터 정책 분석 | 보관 기간 및 사용자 에이전시 설계 |
