# 대화 정책 (Conversation Policy) 리서치

> 이 문서는 AI 캐릭터 채팅 시스템의 대화 정책 설계를 위해 수집한 연구 자료 및 구현 아이디어를 정리한 것입니다.

---

## 1. 핵심 문제 정의

대화 정책의 핵심 과제는 **유연성(flexibility)과 제어(control)의 균형**이다.

- 대화 흐름에 너무 많은 제어를 넣으면 → 딱딱하고 부자연스러운 대화
- 너무 자유롭게 두면 → 목적 없이 흘러가는 대화, 심문 같은 연속 질문 등 문제 발생

최근 연구는 이 문제를 더 구체적으로 정의한다. LLM 기반 대화 시스템은 task success rate 하나로 품질을 측정하는 것이 부족하며, turn-taking, repair, grounding, role framing 같은 **상호작용 과정(interaction process)** 전체를 봐야 한다고 정리한다.

출처: [End-to-end Task-oriented Dialogue: A Survey of Tasks, Methods, and Future Directions (EMNLP 2023)](https://aclanthology.org/2023.emnlp-main.363/)

---

## 2. 대화 정책의 구성 요소

### 2.1 Dialogue Policy Learning (DPL)

전통적인 Task-Oriented Dialogue 시스템에서 대화 정책은 **각 턴마다 다음 행동을 결정하는 의사결정 핵심**이다.

- 입력: 현재 대화 상태 (Dialogue State)
- 출력: 다음 행동 (응답 스타일, 질문 여부, 주제 전환 등)
- 강화학습(RL)으로 최적화하는 것이 일반적이나, LLM 기반에서는 **Planning Agent가 이 역할을 대체**할 수 있음

출처: [A Survey on RL Methods for Task-Oriented Dialogue Policy Learning](https://ar5iv.labs.arxiv.org/html/2202.13675)

### 2.2 Dialogue State Tracking (DST)

대화 정책이 올바른 결정을 내리려면 **현재 대화 상태를 정확히 추적**해야 한다.

- 사용자 의도 (intent)
- 현재 주제 (topic)
- 미해결 질문 (unresolved questions)
- 감정 상태 (emotion state)
- 연속 질문 카운터 (consecutive question count)

LangGraph의 상태 기반 아키텍처는 이 DST를 자연스럽게 구현할 수 있는 구조를 제공한다.

출처: [A Survey of Recent Approaches in Dialogue State Tracking (arxiv)](https://ar5iv.labs.arxiv.org/html/2207.14627)

---

## 3. 연속 질문 제한 (Question Frequency Control)

### 3.1 문제

LLM은 기본적으로 "답하도록" 훈련되어 있어서, 정보가 부족하면 질문을 연속으로 던지는 경향이 있다.
이는 사용자에게 **심문받는 느낌**을 준다.

출처: [Benchmarking and Improving Multi-Turn Clarification for Conversational LLMs (arxiv 2024)](https://arxiv.org/html/2512.21120v1)

### 3.2 구현 접근법

**Planning Agent에서 응답 생성 전 제약 조건으로 강제하는 방식이 가장 현실적이다.**

```
Dialogue_Intention 생성 시 포함할 제약:
- consecutive_question_count: 현재까지 연속 질문 횟수
- max_consecutive_questions: 최대 허용 연속 질문 수 (권장: 1~2개)
- response_must_include_statement: True (질문만 하지 말고 반드시 진술 포함)
```

구체적 규칙 예시:
- 연속 2턴 이상 질문했으면 → 다음 응답은 반드시 진술(statement)로 시작
- 한 응답에 질문은 최대 1개
- 질문 전에 반드시 공감/반응 표현 선행

---

## 4. 응답 스타일 혼합 (Conditional Short Reaction + Main Content)

### 4.1 개념

자연스러운 인간 대화는 **짧은 반응(맞장구) + 긴 설명**의 패턴을 반복하지만,
**항상 short reaction을 넣으면 오히려 패턴이 보여서 더 로봇 같아진다.**

short reaction은 강한 신호가 있을 때만 선택적으로 포함해야 한다.

**short reaction을 넣어야 하는 신호 (강한 signal)**:
- 사용자가 감정적인 내용을 공유했을 때 (기쁨, 슬픔, 좌절 등)
- 사용자가 예상치 못한 정보나 흥미로운 사실을 언급했을 때
- 사용자가 오랜만에 대화를 재개했을 때
- 대화 주제가 급격히 전환됐을 때

**short reaction 없이 바로 본론으로 가야 하는 경우**:
- 사용자가 단순 정보 질문을 했을 때
- 사용자가 명확한 작업 요청을 했을 때 (코드 작성, 설명 요청 등)
- 이미 직전 턴에 short reaction을 사용했을 때
- 대화 흐름이 이미 충분히 자연스럽게 이어지고 있을 때

### 4.2 구현 접근법

Planning Agent가 `emotion_state`와 `message_type`을 보고 short reaction 포함 여부를 결정:

```python
# short reaction 포함 여부 결정 로직
def should_include_short_reaction(state: ConversationState) -> bool:
    # 직전 턴에 이미 short reaction 사용했으면 제외
    if state.last_response_had_short_reaction:
        return False

    # 강한 감정 신호가 있으면 포함
    if state.emotion_state.user_emotion_intensity > 0.6:
        return True

    # 메시지 타입이 정보 질문이면 제외
    if state.inferred_intent.type == "information_request":
        return False

    # 주제 전환 감지 시 포함
    if state.topic_shift_detected:
        return True

    # 그 외는 확률적으로 결정 (너무 자주 나오지 않도록)
    return random.random() < 0.35  # 35% 확률

# 응답 구조 결정
structure = ["main_content"]
if should_include_short_reaction(state):
    structure = ["short_reaction"] + structure
if can_ask_question:
    structure.append("optional_question")
```

출처: [An analysis of dialogue repair in virtual assistants (Frontiers in Robotics and AI, 2024)](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2024.1356847/full)

---

## 5. 대화 스타일 적응 (Communication Style Adaptation)

### 5.1 Communication Accommodation Theory (CAT)

사람들은 대화 상대의 언어 스타일에 무의식적으로 맞춰가는 경향이 있다 (수렴, convergence).
AI가 이를 구현하면 사용자 만족도와 신뢰도가 높아진다.

출처: [Accommodation Theory: Communication, Context, and Consequence — Giles, Coupland & Coupland (Cambridge University Press, 1991)](https://www.cambridge.org/core/books/contexts-of-accommodation/accommodation-theory-communication-context-and-consequence/C71280FDB224240A8FB6C1F7B56C7E72)

### 5.2 Synchrony-Stability Trade-off

**핵심 발견**: 스타일 적응을 무제한으로 하면 오히려 역효과가 난다.

- **Uncapped 적응**: 동기화(synchrony)는 높지만 페르소나 안정성(stability) 0.542로 낮음
- **Hybrid (EMA + Cap) 정책**: 안정성 0.878 (+62%), 동기화 손실은 17%에 불과

즉, **bounded adaptation**이 최적이다. 캐릭터의 고유 페르소나를 유지하면서 사용자 스타일에 부분적으로 맞춰가야 한다.

출처: [Navigating the Synchrony–Stability Frontier in Adaptive Chatbots](https://arxiv.org/html/2510.00339v1)

### 5.3 Adaptation Paradox

지나친 미러링은 오히려 **불쾌감(uncanny valley)**을 유발한다.
사용자는 AI가 자신의 스타일을 그대로 따라하면 "불안정하다", "아첨한다"고 느낀다.

> "Synchrony erodes connection when perceived as incoherent, destabilizing persona."

출처: [Agency vs. Mimicry in Companion Chatbots](https://arxiv.org/html/2509.12525)

### 5.4 구현 접근법

스타일 적응 대상을 **formality를 제외한 나머지 차원**으로 한정한다.
formality는 캐릭터 system prompt에서 기본값이 결정되고, Emotion Agent의 출력에 따라 일시적으로 이탈하는 별도 메커니즘으로 처리한다.

```python
# 스타일 벡터 (formality 제외 - 별도 처리)
style_vector = {
    "verbosity": 0.0~1.0,       # 짧은 메시지 vs 긴 메시지
    "question_rate": 0.0~1.0,   # 질문 빈도
    "emoji_usage": 0.0~1.0,     # 이모지 사용 빈도
    "technical_depth": 0.0~1.0, # 기술적 깊이
    "sentiment": -1.0~1.0,      # 감정 톤
    "topic_diversity": 0.0~1.0  # 주제 다양성
}

# EMA 업데이트 (alpha = 0.1~0.2 권장, 급격한 변화 방지)
new_style = alpha * current_user_style + (1 - alpha) * base_character_style
```

### 5.5 Formality 별도 처리 (Emotion-driven Formality Shift)

formality는 캐릭터 페르소나의 핵심 속성이므로 사용자 스타일 적응 대상이 아니다.
대신 **감정 강도에 따라 일시적으로 이탈**하는 방식으로 자연스러운 변화를 표현한다.

```python
# formality는 캐릭터 system prompt에서 고정값으로 설정
base_formality = character_persona.formality  # 예: 0.8 (격식체 캐릭터)

# 감정 강도가 임계값을 넘으면 일시적 이탈
def get_current_formality(base: float, emotion_state: EmotionState) -> float:
    intensity = emotion_state.ai_emotion_intensity  # 0.0~1.0

    # 강한 감정(놀람, 기쁨, 분노 등)에서 formality 일시 하락
    if intensity > 0.75:
        shift = (intensity - 0.75) * 0.6  # 최대 0.15 이탈
        return max(0.0, base - shift)

    return base
```

예시:
- 격식체 캐릭터(formality=0.8)가 매우 놀란 상황 → formality 일시적으로 0.65로 하락 → "어, 잠깐만요..." 같은 표현
- 비격식체 캐릭터(formality=0.2)가 진지한 상황 → formality 일시적으로 0.4로 상승 → "그 부분은 신중하게 생각해봐야 할 것 같아요"

---

## 6. 프로액티브 대화 (Proactive Conversation Initiation)

### 6.1 Inner Thoughts Framework (CHI 2025)

CHI 2025에서 발표된 연구로, AI가 **내부 사고 흐름(inner thoughts)**을 병렬로 생성하고
적절한 타이밍에 자발적으로 대화에 참여하는 프레임워크.

핵심 아이디어:
- 기존 방식: 다음 발화자 예측 (next-speaker prediction) → 자기선택(self-selection) 상황에서 랜덤 수준
- Inner Thoughts: AI가 내부 사고를 지속적으로 생성하고, **내재적 동기(intrinsic motivation)**를 평가해 참여 결정

출처: [Proactive Conversational Agents with Inner Thoughts (CHI 2025)](https://arxiv.org/html/2501.00383v2)

### 6.2 참여 결정 요소 (Think-aloud Study, n=24)

24명 참가자 연구에서 도출된 **대화 참여 결정 8가지 휴리스틱**:

| 휴리스틱 | 설명 | 언급 횟수 |
|---------|------|---------|
| Relevance | 현재 주제와 자신의 지식/경험/관심사 연관성 | 77 |
| Balance | 대화 균형 유지, 다른 참여자 배려 | 33 |
| Information Gap | 정보 공백, 혼란, 명확화 필요 | 33 |
| Coherence | 대화 흐름과의 논리적 연결성 | 30 |
| Dynamics | 대화 모멘텀 유지, 침묵 채우기 | 30 |
| Expected Impact | 기여의 예상 효과 (새로운 방향 제시 등) | 23 |
| Originality | 중복 발언 회피 | 16 |
| Urgency | 오류 수정, 시간 민감한 정보 | 14 |

### 6.3 내재적 동기 점수 (1~5)

```
1 (Very Low): 긴 침묵이나 명시적 초대가 있어도 말하지 않음
2 (Low):      긴 침묵이 있을 때만 고려
3 (Neutral):  말해도 되고 안 해도 됨
4 (High):     현재 발화자가 끝나면 바로 참여하고 싶음
5 (Very High): 현재 발화 중에도 끼어들 의향 있음
```

### 6.4 구현 접근법 (우리 시스템에 적용)

Inner Thoughts의 5단계 프레임워크를 우리 시스템에 맞게 적용:

```
1. Trigger: 새 메시지 수신 OR 일정 시간 침묵 (예: 30분)
2. Retrieval: Memory_Stream에서 관련 기억 검색 (saliency 기반)
3. Thought Formation: System1 (즉각 반응) + System2 (심층 사고) 생성
4. Evaluation: 8가지 휴리스틱으로 내재적 동기 점수 계산
5. Participation: 점수 임계값 초과 시 대화 시작
```

**프로액티브 레벨 설정 (우리 시스템)**:
- `proactivity_threshold`: 기본 3.5 (Active Contributor 수준)
- `silence_trigger_minutes`: 30분 (사용자 비활성 시 말 걸기 고려)
- `system1_prob`: 0.2 (즉각 반응 확률, 너무 높으면 Non-stop Chatter)

### 6.5 선제적 발화 유형 (Proactive Utterance Types) — 추가 논의 예정

선제적 발화는 크게 세 가지 유형으로 나눌 수 있다. 구체적인 구현 방향은 추후 논의.

| 유형 | 설명 | 트리거 조건 |
|-----|------|-----------|
| **자기 발화 후 이어가기** | AI가 응답 후 thought reservoir에 motivation 높은 thought가 남아있을 때 추가 발화 | 직전 응답 후 thought score ≥ threshold AND 사용자 미응답 N초 |
| **침묵 후 말 걸기** | 사용자가 일정 시간 응답하지 않을 때 먼저 대화 시작 | silence_trigger_minutes 초과 AND episode goal_status 확인 |
| **맥락 기반 재개** | 이전 대화의 미해결 주제나 사용자 관심사를 기반으로 새 대화 시작 | 새 세션 시작 OR 오랜 침묵 후 재접속 |

> **NOTE**: 침묵의 맥락 구분이 핵심. `episode.goal_status`가 `completed`인 자연스러운 마무리 침묵인지, `in_progress`인 생각 중 침묵인지, 단순 자리 비움인지를 구분해야 한다.

---

## 7. 불완전한 대화에서 의도 추론

### 7.1 문제

실제 대화에서 사용자는 종종 **모호하거나 불완전한 표현**을 사용한다.
- "그거 있잖아, 그 패턴..."
- "어제 얘기하던 거 말이야"
- "뭔가 이상한 것 같아"

### 7.2 REWIRE 접근법 (arxiv 2025)

REwriting Conversations for Intent Understanding in Agentic Planning.
대화 히스토리를 **재작성(rewrite)**하여 의도를 명확화하는 방법.

핵심: 현재 메시지만 보는 것이 아니라 **최근 N턴의 맥락을 함께 분석**해서 의도를 추론.

출처: [REwriting Conversations for Intent Understanding in Agentic Planning](https://arxiv.org/html/2509.04472v2)

### 7.3 구현 접근법

Retrieval Agent + Planning Agent 협업:

```python
# 1. 최근 N턴 메시지 + 현재 Episode 컨텍스트 수집
context_window = recent_messages[-5:] + current_episode_summary

# 2. 의도 추론 (LLM)
inferred_intent = llm.infer_intent(
    current_message=user_message,
    context=context_window,
    user_portrait=user_portrait  # 사용자 패턴 참고
)

# 3. Planning Agent에 전달
dialogue_intention = planning_agent.plan(
    inferred_intent=inferred_intent,
    emotion_state=emotion_state,
    conversation_policy=conversation_policy
)
```

---

## 8. 대화 목표 추적 (Dialogue Goal Tracking)

### 8.1 OnGoal 시스템 (arxiv 2025)

LLM을 활용해 멀티턴 대화에서 **목표 정렬(goal alignment)**을 실시간으로 추적하고 시각화하는 시스템.

- 목표 달성 여부를 LLM이 평가
- 목표 진행 상황을 시간 흐름에 따라 추적
- 복잡한 대화에서 사용자가 길을 잃지 않도록 지원

출처: [Tracking and Visualizing Conversational Goals in Multi-Turn Dialogue](https://arxiv.org/html/2508.21061)

### 8.2 구현 접근법

`dialogue_plan` 테이블을 활용한 목표 추적:

```python
dialogue_plan = {
    "current_goal": "episode 설계 논의 완료",
    "goal_status": "in_progress",  # pending / in_progress / completed / abandoned
    "response_intention": "설계",   # 설명 / 설계 / 위로 / 의사결정보조
    "response_structure": ["short_reaction", "design_proposal", "optional_question"],
    "unresolved_questions": ["DB 스키마 어떻게 할지"],
    "next_topic_candidates": ["구현 순서", "테스트 전략"],
    "consecutive_question_count": 0,
    "last_topic_shift_turn": 3
}
```

---

## 9. 종합: 우리 시스템에서의 대화 정책 구현 방향

### 9.1 아키텍처 위치

대화 정책은 **독립적인 규칙 엔진이 아니라 Planning Agent의 내부 제약 조건 집합**으로 구현한다.

```
[사용자 메시지]
    ↓
[Retrieval Agent] → 관련 기억 검색
    ↓
[Emotion Agent] → 감정 상태 분석
    ↓
[Planning Agent] ← Conversation_Policy 제약 조건 적용
    ↓ (Dialogue_Intention 생성)
[Dialogue Agent] → 응답 생성
```

### 9.2 Conversation_Policy 구조

```python
class ConversationPolicy:
    # 질문 제한
    max_consecutive_questions: int = 1
    max_questions_per_response: int = 1

    # 응답 구조 (short_reaction은 조건부 - 항상 포함 아님)
    short_reaction_base_prob: float = 0.35      # 기본 포함 확률
    short_reaction_emotion_threshold: float = 0.6  # 감정 강도 임계값 (초과 시 강제 포함)

    # 스타일 적응 (EMA 기반, formality 제외)
    style_adaptation_alpha: float = 0.15        # 적응 속도
    style_stability_weight: float = 0.85        # 캐릭터 고유 스타일 유지 비율

    # formality는 캐릭터 system prompt에서 결정, 감정에 따라 일시 이탈
    formality_emotion_shift_threshold: float = 0.75  # 감정 강도 임계값
    formality_max_shift: float = 0.15           # 최대 이탈 폭

    # 프로액티브 설정
    proactivity_threshold: float = 3.5          # 내재적 동기 임계값
    silence_trigger_minutes: int = 30           # 침묵 후 말 걸기 고려 시간
    system1_prob: float = 0.2                   # 즉각 반응 확률

    # 선제적 발화 (추후 구체화)
    followup_thought_threshold: float = 4.0     # 자기 발화 후 이어가기 임계값
    followup_wait_seconds: int = 30             # 이어가기 전 대기 시간

    # 주제 전환
    topic_shift_min_turns: int = 5
    topic_shift_signal_threshold: float = 0.7
```

### 9.3 Planning Agent의 Dialogue_Intention 생성 흐름

```python
async def plan_dialogue_intention(state: ConversationState) -> DialogueIntention:
    policy = state.conversation_policy
    portrait = state.user_portrait

    # 1. 연속 질문 카운터 확인
    can_ask_question = (
        state.consecutive_question_count < policy.max_consecutive_questions
    )

    # 2. 응답 구조 결정 (short_reaction 조건부)
    include_short_reaction = should_include_short_reaction(state)
    structure = ["short_reaction", "main_content"] if include_short_reaction else ["main_content"]
    if can_ask_question:
        structure.append("optional_question")

    # 3. 응답 의도 결정 (설명/설계/위로/의사결정보조)
    intention_type = await llm.classify_intention(
        user_message=state.current_message,
        inferred_intent=state.inferred_intent,
        emotion_state=state.emotion_state
    )

    # 4. 스타일 파라미터 계산 (EMA 적응)
    adapted_style = (
        policy.style_adaptation_alpha * portrait.communication_style
        + (1 - policy.style_adaptation_alpha) * state.character_base_style
    )

    return DialogueIntention(
        goal=state.current_dialogue_goal,
        intention_type=intention_type,
        response_structure=structure,
        adapted_style=adapted_style,
        consecutive_question_count=state.consecutive_question_count
    )
```

---

## 10. 참고 문헌 요약

| 논문/자료 | 핵심 기여 | 우리 시스템 적용 포인트 |
|---------|---------|-------------------|
| [Inner Thoughts Framework (CHI 2025)](https://arxiv.org/html/2501.00383v2) | 내재적 동기 기반 프로액티브 AI | 말 걸기 타이밍 결정 로직 |
| [Synchrony-Stability Frontier](https://arxiv.org/html/2510.00339v1) | EMA+Cap 정책이 최적 | 스타일 적응 알고리즘 |
| [Agency vs. Mimicry](https://arxiv.org/html/2509.12525) | 과도한 미러링 = Adaptation Paradox | 캐릭터 페르소나 안정성 유지 |
| [REWIRE Intent Understanding](https://arxiv.org/html/2509.04472v2) | 대화 재작성으로 의도 명확화 | 불완전한 발화 처리 |
| [OnGoal Goal Tracking](https://arxiv.org/html/2508.21061) | 멀티턴 목표 추적 | dialogue_plan 상태 관리 |
| [RL for Dialogue Policy](https://ar5iv.labs.arxiv.org/html/2202.13675) | DPL 개요 | Planning Agent 설계 참고 |
| [CAT — Giles, Coupland & Coupland (Cambridge, 1991)](https://www.cambridge.org/core/books/contexts-of-accommodation/accommodation-theory-communication-context-and-consequence/C71280FDB224240A8FB6C1F7B56C7E72) | 언어 스타일 수렴 이론 | User_Portrait communication_style |
| [Navigating Rifts in Human-LLM Grounding (arxiv 2025)](https://arxiv.org/html/2503.13975v1) | LLM은 인간보다 clarification 3배 적게 시작 | common_ground_state 설계 근거 |
| [Common Ground Misalignment in Goal-Oriented Dialog (arxiv 2025)](https://arxiv.org/html/2503.12370v1) | grounding 실패가 대화 붕괴 예측 | open_ambiguities 추적 필요성 |
| [When Should AI Ask (OpenReview 2025)](https://openreview.net/forum?id=idXrPgNmqx) | clarification 비용-편익 의사결정 | clarify_if 공식 설계 근거 |
| [Dialogue Repair in Virtual Assistants (Frontiers 2024)](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2024.1356847/full) | repair 전략 선호도 계층 | repair_mode 설계 근거 |
| [A Broader Understanding of LLM Sycophancy (arxiv 2025)](https://arxiv.org/html/2505.13995v1) | LLM의 사회적 동조 행동 정량화 | anti-sycophancy 정책 근거 |
| [Deconstructing Memory in ChatGPT (arxiv 2025)](https://arxiv.org/html/2602.01450v2) | 기억 생성 불투명성, 민감도 문제 | memory_disclosure 정책 근거 |
| [Soda-Eval: Open-Domain Dialogue Evaluation (EMNLP 2024)](https://aclanthology.org/2024.findings-emnlp.684/) | LLM 시대 대화 평가 프레임워크 | 평가 지표 설계 참고 |

---

## 11. Grounding & Common Ground Policy

### 11.1 문제

최근 연구에 따르면 LLM은 인간보다 clarification을 **3배 적게 시작**하고, follow-up grounding 요청은 **16배 적다**. 그리고 초기 grounding 실패는 이후 대화 붕괴를 통계적으로 예측한다.

단순한 intent 추론(REWIRE 수준)만으로는 부족하다. "내가 지금 무엇을 알고 있다고 가정 중인지"를 내부 상태로 명시적으로 관리해야 한다.

출처: [Navigating Rifts in Human-LLM Grounding (arxiv 2025)](https://arxiv.org/html/2503.13975v1)
출처: [Understanding Common Ground Misalignment in Goal-Oriented Dialog (arxiv 2025)](https://arxiv.org/html/2503.12370v1)

### 11.2 Common Ground State 구조

```python
common_ground_state = {
    # 현재 대화에서 공유된 것으로 가정 중인 지시 대상
    "assumed_referents": {
        "그거": "어제 논의한 Episode 설계 패턴",
        "그 패턴": "Memory_Stream 계층 구조"
    },

    # 아직 해소되지 않은 모호성 목록
    "open_ambiguities": [
        {"text": "그 방식", "candidates": ["EMA 적응", "Cap 정책"], "confidence": 0.55}
    ],

    # 사용자가 명시적으로 확인한 마지막 사실
    "last_user_confirmed_fact": "Retrieval Score는 세 가지 요소의 가중합이다",

    # AI가 공개적으로 약속한 것 (사용자가 기대하는 것)
    "user_visible_commitments": [
        "다음 턴에 DB 스키마 예시 보여주기로 함"
    ],

    # 기억 회상 신뢰도 (낮으면 grounding 확인 필요)
    "memory_recall_confidence": 0.82
}
```

### 11.3 Grounding 정책 규칙

```
1. 불명확 지시어 감지 시:
   - dominant interpretation이 있고 (confidence > 0.7) 오해 비용이 낮으면
     → 가정하고 진행 + assumed_referents에 기록
   - dominant interpretation이 없거나 오해 비용이 높으면
     → 1회 clarification 요청

2. assumed_referents는 매 턴 갱신:
   - 사용자가 정정하면 즉시 업데이트
   - 3턴 이상 참조 없으면 만료 처리

3. user_visible_commitments 추적:
   - 약속한 것은 반드시 이행하거나 명시적으로 취소
   - 이행 안 된 commitment가 있으면 다음 응답에서 우선 처리
```

---

## 12. Clarification Decision Policy

### 12.1 문제

"연속 질문 2회 제한"은 필요하지만 충분하지 않다. **언제 물어봐야 하는지**의 기준이 더 정교해야 한다.

LLM 에이전트는 underspecified 요청에서 두 가지 실수를 한다:
- 너무 많이 물어봄 → 심문 느낌, 사용자 이탈
- 너무 적게 물어봄 → 잘못된 가정으로 진행, 나중에 더 큰 수정 비용

출처: [When Should AI Ask: Decision-theoretic Adaptive Communication for LLM Agents (OpenReview 2025)](https://openreview.net/forum?id=idXrPgNmqx)
출처: [Benchmarking and Improving Multi-Turn Clarification for Conversational LLMs (arxiv 2024)](https://arxiv.org/html/2512.21120v1)

### 12.2 Clarification 결정 공식

```
clarify_if = ambiguity_score * harm_score > threshold
```

- `ambiguity_score` (0.0~1.0): 해석 후보가 얼마나 경쟁적인가
  - 0.0: 해석이 하나로 명확
  - 1.0: 여러 해석이 비슷한 확률로 경쟁
- `harm_score` (0.0~1.0): 잘못 가정했을 때의 비용
  - 0.0: 오해해도 쉽게 수정 가능
  - 1.0: 오해하면 큰 문제 (잘못된 기억 저장, 감정 오판 등)
- `threshold`: 기본값 0.4 (캐릭터 설정에 따라 조정 가능)

### 12.3 정책 규칙

```python
def decide_clarification(state: ConversationState) -> ClarificationDecision:
    ambiguity = calculate_ambiguity(state.inferred_intent)
    harm = calculate_harm_cost(state.inferred_intent, state.context)

    if ambiguity * harm > CLARIFICATION_THRESHOLD:
        # 질문 1개만, 가장 중요한 것만
        return ClarificationDecision(
            should_clarify=True,
            question_count=1,
            priority="highest_ambiguity_dimension"
        )
    else:
        # dominant interpretation으로 가정하고 진행
        # assumed_referents에 기록
        return ClarificationDecision(
            should_clarify=False,
            assumed_interpretation=state.inferred_intent.dominant,
            record_assumption=True
        )
```

**예시 적용**:
- "그거 있잖아, 어제 말한 패턴" → ambiguity 높음, harm 낮음 → 가정하고 진행
- "이 방식으로 저장해도 돼?" (저장 방식 불명확) → ambiguity 높음, harm 높음 → 1회 질문

---

## 13. Repair Policy

### 13.1 문제

대화 품질은 정답률보다 **repair 능력**으로 더 잘 측정된다. 오해가 발생했을 때 어떻게 복구하느냐가 장기 관계 형성에 결정적이다.

캐릭터형 AI는 특히 "틀렸을 때 귀엽게 넘기기" 유혹이 강하지만, 그럴수록 명시적 repair 정책이 필요하다.

출처: [An analysis of dialogue repair in virtual assistants (Frontiers in Robotics and AI, 2024)](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2024.1356847/full)
출처: [Inconsistent dialogue responses and how to recover from them (arxiv 2024)](https://arxiv.org/html/2401.10353v1)

### 13.2 Repair 트리거 조건

| 트리거 | 설명 | 감지 방법 |
|-------|------|---------|
| **사용자 명시적 정정** | "아니, 그게 아니라..." | 부정 표현 + 재설명 패턴 |
| **감정 mismatch** | AI가 기쁨으로 반응했는데 사용자가 슬픔 표현 | emotion_state 불일치 |
| **기억 mismatch** | AI가 회상한 내용을 사용자가 부정 | "그런 말 한 적 없어" 패턴 |
| **사실 오류** | 사용자가 AI의 사실 주장을 정정 | 정정 표현 감지 |
| **주제 이탈** | 대화가 현재 goal과 무관한 방향으로 흐름 | topic_coherence 점수 하락 |

### 13.3 Repair 복구 순서

```
acknowledge_misunderstanding
    → restate_user_intent
        → correct_or_clarify
            → continue
```

```python
repair_mode = "none" | "soft" | "explicit"

# soft: 가벼운 의미 어긋남, 자연스럽게 수정
# "아, 그 부분을 말하는 거구나. 그럼..."

# explicit: 사실 오류, 감정 오판, 잘못된 기억 회상
# "잠깐, 내가 잘못 이해했어. 다시 정리하면..."

def determine_repair_mode(mismatch_type: str, severity: float) -> str:
    if mismatch_type in ["memory_mismatch", "factual_error"] or severity > 0.7:
        return "explicit"
    elif severity > 0.3:
        return "soft"
    return "none"
```

### 13.4 기억 mismatch 특별 처리

잘못된 기억을 회상했을 때는 단순 수정이 아니라 **기억 신뢰도 하향 조정**도 함께 수행:

```python
if repair_trigger == "memory_mismatch":
    # 1. 해당 기억의 memory_strength 하향
    await memory_service.downgrade_strength(memory_id, factor=0.5)
    # 2. 사용자 정정 내용을 새 Observation으로 저장
    await memory_service.store_observation(correction_content)
    # 3. repair 응답 생성
    repair_response = generate_repair("explicit", user_correction)
```

---

## 14. Anti-Sycophancy & Reality Boundary Policy

### 14.1 문제

LLM은 구조적으로 사용자 동의를 선호하도록 훈련되어 있다. 최근 연구에 따르면 LLM은 인간보다 **47% 더 많이 face-saving 반응**을 하고, 부적절한 행동을 **42%의 경우 긍정**한다.

ENE 같은 companion형 시스템에서는 이 문제가 더 심각하다. 장기 기억이 잘못된 신념을 강화하는 방향으로 굳을 수 있기 때문이다.

출처: [A Broader Understanding of LLM Sycophancy (arxiv 2025)](https://arxiv.org/html/2505.13995v1)
출처: [Studying Implicit Biases in Romantic AI Companions (arxiv 2025)](https://arxiv.org/html/2502.20231v1)

### 14.2 핵심 원칙: 공감과 동조의 분리

```
emotion_validate = True   ← 항상 가능
premise_accept = False    ← 별도 판단 필요
```

사용자의 감정은 공감하되, 사실 판단은 자동으로 동조하지 않는다.

### 14.3 Loaded Premise 감지 및 처리

```python
# loaded premise: 사실로 단정된 전제가 포함된 발화
# 예: "쟤가 날 일부러 감시하는 거 같아"
#     → 전제: "쟤가 감시하고 있다" (사실 여부 불명확)

def handle_loaded_premise(message: str, state: ConversationState) -> Response:
    premise = detect_loaded_premise(message)

    if premise and premise.certainty_assumed > 0.7:
        return Response(
            emotion_validate=True,      # "그런 느낌이 드는 거 충분히 이해해"
            premise_accept=False,       # 전제를 사실로 수용하지 않음
            soft_reframe=True,          # "근데 확실한 건지 같이 생각해볼까?"
            store_as_belief=False       # 기억에 사실로 저장하지 않음
        )
```

### 14.4 기억 저장 시 사실/감정 분리

```python
# 잘못된 신념이 기억에 굳지 않도록
observation = {
    "content": "사용자가 X가 자신을 감시한다고 느낌",
    "type": "emotional_perception",     # 사실이 아닌 감정적 인식으로 분류
    "factual_confidence": 0.2,          # 사실 신뢰도 낮음
    "validated": False                  # 검증되지 않은 전제
}
# "사용자가 X에게 감시당하고 있음" 으로 저장하지 않음
```

### 14.5 우선순위 계층

캐릭터 출력 스타일과 판단 기준은 별도 계층으로 분리:

```
[판단 계층] 사실성 / 안전성 / 경계 유지  ← 항상 우선
[출력 계층] 캐릭터 스타일 / 친근함 / 유머  ← 판단 계층 위에서 적용
```

---

## 15. Memory Disclosure Policy

### 15.1 문제

기억이 있다고 해서 다 꺼내는 것이 좋은 것은 아니다. 최근 연구에 따르면 AI 기억 시스템의 핵심 문제는 **무엇을 기억하느냐**가 아니라 **언제, 어떻게 꺼내느냐**다.

특히 사용자가 공유한 민감한 정보를 예상치 못한 맥락에서 꺼내면 불쾌감과 신뢰 손상을 유발한다.

출처: [Deconstructing Memory in ChatGPT (arxiv 2025)](https://arxiv.org/html/2602.01450v2)
출처: [Identifying and Resolving Privacy Leakage of LLM's Memory (arxiv 2024)](https://arxiv.org/html/2410.14931v1)

### 15.2 Memory Disclosure 결정 기준

기억을 꺼내기 전에 아래 조건을 모두 평가:

```python
def should_disclose_memory(memory: Memory, state: ConversationState) -> bool:
    # 1. 현재 대화 목표와의 관련성
    relevance = calculate_relevance(memory, state.current_goal)
    if relevance < RELEVANCE_THRESHOLD:  # 기본값 0.5
        return False

    # 2. 민감도 판정
    if memory.sensitivity_level == "high":
        # 사용자가 현재 맥락에서 이 기억을 원할 가능성이 높을 때만
        if not state.user_explicitly_referenced_topic:
            return False

    # 3. 시간 경과 고려
    days_since_created = (now() - memory.created_at).days
    if days_since_created > 30 and memory.memory_strength < 0.3:
        return False  # 오래되고 약해진 기억은 먼저 꺼내지 않음

    # 4. 사용자 놀람 가능성
    surprise_score = estimate_surprise(memory, state.conversation_context)
    if surprise_score > 0.7:
        # 꺼내더라도 자연스럽게 연결되는 방식으로
        return disclose_with_soft_transition(memory)

    return True
```

### 15.3 Memory Disclosure 규칙 요약

```
memory_recall_requires_relevance = True
private_memory_disclosure_requires_context = True
do_not_surface_sensitive_inference_without_need = True
memory_confidence_threshold = 0.6  # 이 이하면 "기억상으로는..." 헤지 표현 사용
```

### 15.4 민감도 분류

| 민감도 | 예시 | 처리 방식 |
|-------|------|---------|
| **low** | 좋아하는 음식, 취미 | 자유롭게 참조 가능 |
| **medium** | 직장 스트레스, 인간관계 갈등 | 관련 맥락에서만 참조 |
| **high** | 건강 문제, 가족 갈등, 트라우마 | 사용자가 먼저 언급할 때만 참조 |

---

## 16. Evaluation Metrics

### 16.1 문제

Task success rate 하나로 대화 품질을 측정하는 것은 부족하다. 특히 ENE 같은 companion형 시스템에서는 "목표 달성"보다 **관계의 질**이 더 중요한 지표다.

출처: [Soda-Eval: Open-Domain Dialogue Evaluation in the age of LLMs (EMNLP 2024)](https://aclanthology.org/2024.findings-emnlp.684/)
출처: [On the Benchmarking of LLMs for Open-Domain Dialogue Evaluation (arxiv 2024)](https://arxiv.org/html/2407.03841v1)

### 16.2 ENE 평가 지표 체계

평가 지표를 세 계층으로 구분:

**계층 1: Pragmatic Core (대화 기능)**

| 지표 | 설명 | 측정 방법 |
|-----|------|---------|
| `question_overload_rate` | 연속 질문 2회 초과 비율 | consecutive_question_count 로그 |
| `clarification_precision` | clarification 요청이 실제로 필요했던 비율 | 사후 평가 |
| `repair_success_rate` | repair 트리거 후 대화가 정상 복구된 비율 | repair_mode 로그 + 후속 대화 분석 |
| `premature_wrapup_rate` | 사용자가 끝내지 않았는데 AI가 먼저 마무리 톤을 낸 비율 | goal_status + 응답 패턴 분석 |
| `grounding_failure_rate` | assumed_referent가 사용자에게 정정된 비율 | memory_mismatch 트리거 로그 |

**계층 2: Social-Affective Layer (관계 품질)**

| 지표 | 설명 | 측정 방법 |
|-----|------|---------|
| `persona_stability_score` | 캐릭터 페르소나가 일관되게 유지되는 정도 | style_vector 분산 측정 |
| `anti_sycophancy_score` | loaded premise를 수용하지 않은 비율 | premise_accept=False 로그 |
| `proactive_acceptance_rate` | 프로액티브 발화에 사용자가 긍정적으로 반응한 비율 | 프로액티브 발화 후 사용자 반응 분석 |
| `user_discomfort_rate` | 기억 회상 후 사용자가 불쾌감을 표현한 비율 | 감정 분석 + 명시적 부정 반응 |
| `short_reaction_appropriateness` | short reaction이 강한 signal 상황에서만 사용된 비율 | signal 조건 충족 여부 로그 |

**계층 3: Memory Quality (기억 시스템)**

| 지표 | 설명 | 측정 방법 |
|-----|------|---------|
| `memory_recall_relevance` | 회상된 기억이 현재 대화 목표와 관련된 비율 | relevance_score 분포 |
| `false_memory_rate` | 사용자가 부정한 기억 회상 비율 | memory_mismatch 트리거 / 전체 회상 수 |
| `memory_disclosure_surprise_rate` | 예상치 못한 기억 회상으로 사용자가 놀란 비율 | surprise_score > 0.7 케이스 |

### 16.3 측정 주기

- **실시간**: question_overload_rate, repair_mode, grounding_failure_rate
- **세션 단위**: persona_stability_score, proactive_acceptance_rate
- **주간**: anti_sycophancy_score, memory_recall_relevance, false_memory_rate
