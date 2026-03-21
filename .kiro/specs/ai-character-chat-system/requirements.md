# Requirements Document

## Introduction

AI 캐릭터 채팅 시스템은 사용자가 자연스럽게 대화할 수 있는 AI 캐릭터를 제공하는 시스템입니다. WebSocket 기반의 실시간 채팅으로 시작하여, 추후 음성 대화로 확장 가능하도록 설계됩니다. 시스템은 캐릭터 페르소나, 대화 기억, 감정 인식, 개인화된 주제 추천 등의 기능을 통해 사람과 같은 자연스러운 대화 경험을 제공합니다.

## Glossary

- **Chat_System**: AI 캐릭터와 사용자 간의 대화를 관리하는 전체 시스템
- **LLM_Adapter**: 클라우드 API(OpenAI, Anthropic 등)와 로컬 모델(Ollama, LM Studio 등)을 포함한 다양한 LLM 제공자를 추상화하는 플러그인 기반 인터페이스 계층
- **LLM_Provider**: LLM_Adapter에 연결되는 개별 LLM 구현체 (플러그인)
- **Character_Persona**: 캐릭터의 성격, 말투, 행동 패턴을 정의하는 설정
- **Memory_System**: 대화 내용을 저장하고 검색하는 RAG 기반 시스템
- **Memory_Stream**: 모든 경험을 시간순으로 저장하는 기억 흐름 (Generative Agents 아키텍처)
- **Observation**: 대화에서 추출된 검색 친화적 사건 표현
- **Importance_Score**: 각 기억의 중요도를 나타내는 수치 (0.0~1.0)
- **Retrieval_Score**: Recency + Importance + Relevance의 가중합으로 계산되는 검색 점수
- **Reflection**: 원시 observation으로부터 추론된 상위 의미와 패턴 (예: 사용자 선호도, 목표, 관계)
- **Episode**: 의미 있는 사건 묶음으로, 목적, 전환점, 결론, 감정 변화, 중요도를 포함
- **User_Portrait**: 사용자의 성격, 의사소통 스타일, 관심사, 선호도를 통합한 프로필
- **Memory_Strength**: 시간과 접근 빈도에 따라 변화하는 기억의 강도
- **Memory_Evolution**: 시간 경과와 사용 패턴에 따라 기억이 강화되거나 약화되는 과정
- **Forgetting_Curve**: 에빙하우스 망각곡선을 참고한 기억 감쇠 메커니즘
- **Dialogue_Intention**: 현재 대화의 목표와 응답 전략
- **Emotion_Agent**: 대화에서 감정을 분석하고 관리하는 에이전트
- **Topic_Recommender**: 사용자 선호도를 분석하여 대화 주제를 추천하는 컴포넌트
- **WebSocket_Server**: 실시간 양방향 통신을 제공하는 서버
- **Conversation_Policy**: 자연스러운 대화를 위한 규칙과 전략 — Planning Agent에 주입되는 설정 객체로 구현
- **Common_Ground_State**: 대화 참여자 간 공유된 것으로 가정 중인 지식과 지시 대상의 집합
- **Assumed_Referents**: 현재 대화에서 AI가 공유된 것으로 가정 중인 지시 대상 (예: "그거" → "어제 논의한 패턴")
- **Clarification_Decision**: 모호한 발화에 대해 질문할지 가정하고 진행할지 결정하는 정책 (ambiguity_score * harm_score > threshold)
- **Repair_Policy**: 오해, 감정 불일치, 기억 오류 발생 시 대화를 복구하는 정책 (acknowledge → restate → correct → continue)
- **Repair_Mode**: 복구 강도 수준 — none(복구 불필요), soft(가벼운 수정), explicit(명시적 정정)
- **Anti_Sycophancy**: 사용자의 감정은 공감하되 사실 판단은 자동 동조하지 않는 원칙
- **Loaded_Premise**: 사실로 단정된 전제가 포함된 발화 (예: "쟤가 날 감시하는 거 같아")
- **Emotional_Snapshot**: Observation/Episode 저장 시 함께 기록되는 그 시점의 감정 상태 스냅샷
- **Emotional_Valence**: 감정의 긍정/부정 강도 (-1.0 부정 ~ 1.0 긍정)
- **Emotional_Alignment**: 사용자-AI 감정 일치도 (0.0~1.0)
- **Disclosure_Weight**: 기억의 출현도 가중치 — Retrieval Score에 곱해져 억제된 기억이 자연스럽게 하위권으로 밀림
- **Memory_Suppression**: 삭제 대신 disclosure_weight를 낮춰 기억의 출현 빈도를 억제하는 메커니즘
- **Emotion_State**: 기쁨, 슬픔, 분노 등 다차원 감정 수치
- **FastAPI**: 비동기 처리와 WebSocket을 지원하는 Python 웹 프레임워크
- **LangGraph**: 상태 기반 에이전트 오케스트레이션을 제공하는 멀티 에이전트 프레임워크
- **LangChain**: LLM 추상화 계층을 제공하는 통합 프레임워크
- **pgvector**: PostgreSQL의 벡터 검색 확장 기능
- **Context_Window**: LLM이 한 번에 처리할 수 있는 최대 토큰 수

## Requirements

### Requirement 1: LLM 추상화 계층

**User Story:** As a 개발자, I want 클라우드 API와 로컬 모델을 포함한 다양한 LLM 제공자를 플러그인 방식으로 쉽게 교체할 수 있는 추상화 계층, so that 시스템이 특정 LLM 벤더에 종속되지 않고 유연하게 확장할 수 있다

#### Acceptance Criteria

1. THE LLM_Adapter SHALL 통일된 인터페이스를 통해 텍스트 생성 요청을 처리한다
2. THE LLM_Adapter SHALL 클라우드 기반 LLM 제공자(OpenAI, Anthropic, Google 등)를 지원한다
3. THE LLM_Adapter SHALL 로컬 LLM 제공자(Ollama, LM Studio, LocalAI 등)를 지원한다
4. THE LLM_Adapter SHALL 플러그인 방식으로 새로운 LLM_Provider를 등록하고 사용할 수 있다
5. WHEN 새로운 LLM_Provider가 추가되면, THE LLM_Adapter SHALL 기존 코드 수정 없이 해당 제공자를 사용할 수 있다
6. WHEN LLM 요청이 발생하면, THE LLM_Adapter SHALL 선택된 LLM_Provider에게 요청을 표준 형식으로 전달한다
7. WHEN LLM_Provider가 응답을 반환하면, THE LLM_Adapter SHALL 응답을 표준 형식으로 변환하여 반환한다
8. IF LLM_Provider 호출이 실패하면, THEN THE LLM_Adapter SHALL 에러 정보를 포함한 표준 에러 응답을 반환한다
9. THE LLM_Adapter SHALL 런타임에 LLM_Provider를 동적으로 전환할 수 있다

### Requirement 2: 캐릭터 페르소나 설정

**User Story:** As a 사용자, I want AI가 특정 캐릭터처럼 일관된 성격으로 대화하기를, so that 더 몰입감 있고 개성 있는 대화 경험을 할 수 있다

#### Acceptance Criteria

1. THE Chat_System SHALL 캐릭터별 시스템 프롬프트를 저장하고 관리한다
2. WHEN 대화가 시작되면, THE Chat_System SHALL 선택된 캐릭터의 페르소나 설정을 LLM 요청에 포함한다
3. THE Character_Persona SHALL 캐릭터의 말투, 성격, 배경 스토리, 행동 패턴을 정의한다
4. THE Chat_System SHALL 대화 중 캐릭터 페르소나를 일관되게 유지한다
5. THE Chat_System SHALL 여러 캐릭터 페르소나를 지원하고 전환 가능하도록 구현된다

### Requirement 3: 대화 기억 시스템 (Memory Stream & Retrieval)

**User Story:** As a AI 캐릭터, I want 과거 대화 내용을 기억하고 참조할 수 있기를, so that 맥락 있고 연속성 있는 대화를 할 수 있다

#### Acceptance Criteria

1. WHEN 대화 메시지가 생성되면, THE Memory_System SHALL 메시지를 Observation으로 변환하여 Memory_Stream에 저장한다
2. THE Memory_System SHALL 각 Observation에 creation_time, last_access_time, Importance_Score 메타데이터를 포함한다
3. THE Memory_System SHALL Importance_Score를 0.0에서 1.0 사이의 값으로 자동 계산하여 할당한다
4. THE Memory_System SHALL 계층적 메모리 구조를 유지한다: 원본 Message → Observation → Episode → Reflection
5. WHEN AI가 응답을 생성할 때, THE Memory_System SHALL Retrieval_Score 기반으로 관련 기억을 검색하여 컨텍스트로 제공한다
6. THE Memory_System SHALL Retrieval_Score를 Recency, Importance, Relevance의 가중합으로 계산한다
7. THE Memory_System SHALL 벡터 임베딩을 사용하여 Relevance(의미적 유사도)를 계산한다
8. WHEN Observation이 검색되면, THE Memory_System SHALL last_access_time을 업데이트하여 Recency를 반영한다
9. THE Memory_System SHALL Episode를 "의미 있는 사건 묶음"으로 정의하고 관리한다
10. THE Memory_System SHALL 각 Episode에 목적, 전환점, 결론, 감정 변화, 중요도를 포함한다
11. WHEN 새로운 대화가 저장되면, THE Memory_System SHALL 자동으로 Keyword를 추출하여 인덱싱한다
12. THE Memory_System SHALL Observation, Episode, Reflection 모두를 검색 대상으로 포함한다

### Requirement 3.5: Reflection 시스템 (상위 의미 추론)

**User Story:** As a AI 캐릭터, I want 원시 대화 기억으로부터 상위 의미와 패턴을 추론하기를, so that 사용자를 더 깊이 이해하고 맥락 있는 대화를 할 수 있다

#### Acceptance Criteria

1. THE Memory_System SHALL Reflection을 "요약"이 아닌 "상위 의미 추론"으로 생성한다
2. THE Memory_System SHALL Reflection을 통해 사용자 패턴, 선호도, 목표, 관계를 추론한다
3. WHEN Importance_Score의 누적 합이 임계값에 도달하면, THE Memory_System SHALL 자동으로 Reflection을 생성한다
4. THE Memory_System SHALL Reflection 자체도 Observation과 동일하게 검색 대상으로 포함한다
5. THE Memory_System SHALL 각 Reflection에 Importance_Score를 할당한다
6. THE Memory_System SHALL Reflection을 Memory_Stream에 저장하여 시간순 기억 흐름에 포함한다
7. WHEN Reflection이 생성되면, THE Memory_System SHALL 해당 Reflection의 근거가 된 Observation들을 참조로 기록한다
8. THE Memory_System SHALL Reflection 예시를 포함한다: "사용자는 구조 설계를 선호한다", "사용자는 실무 적용 가능성을 중요하게 본다"

### Requirement 3.7: User Portrait & Memory Evolution (사용자 프로필 및 기억 진화)

**User Story:** As a AI 캐릭터, I want 사용자에 대한 통합된 프로필을 형성하고 시간에 따라 기억을 진화시키기를, so that 더 깊이 있고 일관된 사용자 이해를 유지할 수 있다

#### Acceptance Criteria

**User Portrait**
1. THE Memory_System SHALL 사용자별 User_Portrait를 생성하고 관리한다
2. THE User_Portrait SHALL 성격 특성, 의사소통 스타일, 관심사, 선호도를 포함한다
3. WHEN Reflection이 생성되면, THE Memory_System SHALL User_Portrait를 업데이트한다
4. THE Chat_System SHALL User_Portrait를 응답 생성 시 참고하여 개인화된 대화를 제공한다
5. THE User_Portrait SHALL 신뢰도 점수(confidence_score)를 포함하여 프로필의 확실성을 나타낸다
6. THE Memory_System SHALL 계층적 사용자 이해를 유지한다: Level 1 (사실 기억 - Observation), Level 2 (패턴 추론 - Reflection), Level 3 (사용자 프로필 - Portrait)

**Memory Evolution**
7. THE Memory_System SHALL 시간 경과에 따라 기억의 강도를 조정한다 (망각 곡선 기반)
8. WHEN 기억이 반복적으로 접근되면, THE Memory_System SHALL 해당 기억의 Memory_Strength를 증가시킨다
9. WHEN 기억이 오래 접근되지 않으면, THE Memory_System SHALL 해당 기억의 강도를 감소시킨다
10. THE Memory_System SHALL Memory_Strength를 계산할 때 Importance_Score와 시간 감쇠를 결합한다
11. THE Memory_System SHALL Forgetting_Curve를 적용하여 오래된 기억의 검색 우선순위를 낮춘다

**Memory Suppression (출현도 억제)**
12. WHEN 사용자가 특정 기억을 꺼내지 말라고 요청하면, THE Memory_System SHALL 해당 기억을 삭제하지 않고 Disclosure_Weight를 대폭 낮춘다
13. THE Memory_System SHALL Retrieval Score 계산 시 `base_score * disclosure_weight`를 적용하여 억제된 기억이 자연스럽게 하위권으로 밀리도록 한다
14. WHEN 사용자가 억제된 기억의 주제를 직접 언급하면, THE Memory_System SHALL 해당 기억을 일시적으로 재활성화한다
15. THE Memory_System SHALL suppression_reason을 기록하여 억제 이유를 추적한다

**Emotional Snapshot**
16. WHEN Observation이 저장되면, THE Memory_System SHALL 그 시점의 Emotional_Snapshot을 함께 저장한다
17. THE Emotional_Snapshot SHALL user_emotion_snapshot, ai_emotion_snapshot(상세 수치), emotional_valence, emotional_arousal, emotional_alignment(요약 지표)를 포함한다
18. WHEN Episode가 완료되면, THE Memory_System SHALL 포함된 Observation들의 emotional_valence 평균을 avg_emotional_valence로 저장한다
19. THE Memory_System SHALL emotional_valence가 높은 기억을 프로액티브 발화 시 우선 참조한다
20. THE Memory_System SHALL emotional_alignment가 낮은 기억을 감정 오판 학습 데이터로 활용한다

### Requirement 4: 자연스러운 대화 정책

**User Story:** As a 사용자, I want AI가 사람처럼 자연스럽게 대화하기를, so that 로봇 같지 않은 편안한 대화를 나눌 수 있다

#### Acceptance Criteria

**질문 제한 및 Clarification**
1. THE Conversation_Policy SHALL 연속된 질문의 개수를 제한하여 심문 같은 대화를 방지한다 (최대 연속 1회)
2. WHEN 모호한 발화가 감지되면, THE Chat_System SHALL `ambiguity_score * harm_score > threshold` 공식으로 질문 여부를 결정한다
3. WHEN 오해 비용이 낮고 지배적 해석이 있으면, THE Chat_System SHALL 가정하고 진행하며 assumed_referents에 기록한다
4. WHEN 질문이 필요하면, THE Chat_System SHALL 한 번에 하나의 질문만 한다

**응답 구조**
5. THE Chat_System SHALL short reaction(맞장구, 공감 표현)을 강한 신호가 있을 때만 조건부로 포함한다
6. WHEN 사용자가 감정적 내용을 공유하거나 주제가 급격히 전환되면, THE Chat_System SHALL short reaction을 포함한다
7. WHEN 사용자가 단순 정보 질문이나 명확한 작업 요청을 하면, THE Chat_System SHALL short reaction 없이 바로 본론으로 응답한다
8. WHEN 직전 턴에 이미 short reaction을 사용했으면, THE Chat_System SHALL 다음 턴에는 short reaction을 포함하지 않는다

**Grounding & Common Ground**
9. THE Chat_System SHALL 대화 중 Common_Ground_State를 유지하여 assumed_referents, open_ambiguities, user_visible_commitments를 추적한다
10. WHEN AI가 공개적으로 약속한 것(user_visible_commitments)이 있으면, THE Chat_System SHALL 해당 약속을 이행하거나 명시적으로 취소한다
11. WHEN assumed_referent가 사용자에게 정정되면, THE Chat_System SHALL 즉시 Common_Ground_State를 업데이트한다

**Repair Policy**
12. WHEN 오해, 감정 불일치, 기억 오류, 사실 오류가 감지되면, THE Chat_System SHALL Repair_Policy를 적용한다
13. THE Chat_System SHALL repair를 acknowledge → restate → correct → continue 순서로 수행한다
14. THE Chat_System SHALL repair_mode를 none / soft / explicit 중 심각도에 따라 결정한다
15. WHEN 기억 mismatch로 repair가 발생하면, THE Chat_System SHALL 해당 기억의 memory_strength를 하향 조정한다

**Anti-Sycophancy**
16. THE Chat_System SHALL 사용자의 감정은 공감하되 사실 판단은 자동으로 동조하지 않는다 (emotion_validate=True, premise_accept=별도 판단)
17. WHEN Loaded_Premise가 감지되면, THE Chat_System SHALL 전제를 사실로 수용하지 않고 부드럽게 재구성한다
18. THE Chat_System SHALL Loaded_Premise를 사실로 기억에 저장하지 않는다

**스타일 적응**
19. THE Conversation_Policy SHALL 사용자의 대화 스타일을 EMA 기반으로 학습하되 캐릭터 고유 스타일을 유지한다 (bounded adaptation)
20. THE Conversation_Policy SHALL formality를 스타일 적응 대상에서 제외하고 캐릭터 system prompt에서 기본값을 고정한다
21. WHEN AI 감정 강도가 임계값을 초과하면, THE Chat_System SHALL formality를 일시적으로 이탈시킨다

**프로액티브 대화**
22. WHEN 사용자가 일정 시간 응답하지 않으면, THE Chat_System SHALL 내재적 동기 점수를 평가하여 먼저 대화를 시작할 수 있다
23. THE Chat_System SHALL "정보 제공자"가 아닌 "생각을 함께 이어가는 동반자"로서 대화한다
24. THE Conversation_Policy SHALL 불완전한 대화에서도 사용자의 의도와 맥락을 추론한다

### Requirement 4.5: Planning & Dialogue Intention (대화 수준 계획)

**User Story:** As a AI 캐릭터, I want 현재 대화의 목표와 의도를 계획하고 추적하기를, so that 일관되고 목적 있는 대화를 진행할 수 있다

#### Acceptance Criteria

1. WHEN 대화가 시작되거나 주제가 전환되면, THE Chat_System SHALL 현재 대화의 목표를 설정한다
2. THE Chat_System SHALL Dialogue_Intention을 통해 응답 의도를 계획한다: 설명, 설계, 위로, 의사결정 보조 등
3. THE Chat_System SHALL 사용자의 장기 작업 흐름을 이해하고 이전 대화와 연결한다
4. WHEN 응답을 생성하기 전에, THE Chat_System SHALL 현재 대화 목표와 응답 의도를 고려한다
5. THE Chat_System SHALL 대화 종료 후 남길 상태를 관리한다: 미해결 질문, 다음 논의 주제, 사용자 감정 상태 등
6. THE Chat_System SHALL Dialogue_Intention 예시를 포함한다: "현재 목표: episode 설계 논의 완료", "응답 스타일: 짧은 확답 → 구조 제안 → DB 영향 설명"
7. WHEN 대화 목표가 달성되면, THE Chat_System SHALL 자연스럽게 대화를 마무리하거나 새로운 목표로 전환한다
8. THE Chat_System SHALL 사용자의 현재 작업 맥락을 추적하여 관련 있는 과거 대화를 연결한다
9. THE Chat_System SHALL 대화 계획 이력을 저장하여 사용자의 작업 패턴을 학습한다

### Requirement 5: 감정 인식 및 관리 시스템

**User Story:** As a AI 캐릭터, I want 사용자와 나의 감정 상태를 이해하고 반영하기를, so that 감정적으로 공감하고 반응하는 대화를 할 수 있다

#### Acceptance Criteria

1. THE Emotion_Agent SHALL 다차원 감정 수치(기쁨, 슬픔, 분노, 놀람, 두려움, 혐오)를 관리한다
2. WHEN 사용자 메시지가 수신되면, THE Emotion_Agent SHALL 사용자의 감정 상태를 분석하여 수치화한다
3. THE Emotion_Agent SHALL AI 캐릭터의 현재 감정 상태를 유지하고 대화에 따라 업데이트한다
4. WHEN AI가 응답을 생성할 때, THE Chat_System SHALL 현재 감정 상태를 반영하여 응답을 생성한다
5. THE Emotion_Agent SHALL 감정 변화 이력을 저장하여 감정의 연속성을 유지한다
6. THE Chat_System SHALL 감정 수치에 따라 응답의 톤, 어휘 선택, 문장 구조를 조정한다

### Requirement 6: 개인화된 주제 추천

**User Story:** As a AI 캐릭터, I want 사용자가 관심 있어 할 주제를 발견하고 제안하기를, so that 대화가 더 흥미롭고 지속 가능하다

#### Acceptance Criteria

1. THE Topic_Recommender SHALL 대화 내용을 분석하여 사용자의 관심사를 추출한다
2. THE Topic_Recommender SHALL AWS 클라우드 환경에서 백그라운드로 실행된다
3. WHEN 새로운 관심 주제가 발견되면, THE Topic_Recommender SHALL Memory_System에 주제 정보를 업데이트한다
4. THE Chat_System SHALL 적절한 타이밍에 추천된 주제를 자연스럽게 대화에 포함한다
5. THE Topic_Recommender SHALL 사용자의 반응을 학습하여 주제 추천 정확도를 개선한다
6. THE Topic_Recommender SHALL 외부 정보 소스를 활용하여 최신 트렌드와 관련된 주제를 발견한다

### Requirement 7: WebSocket 실시간 통신

**User Story:** As a 사용자, I want 실시간으로 메시지를 주고받기를, so that 자연스러운 대화 흐름을 경험할 수 있다

#### Acceptance Criteria

1. THE WebSocket_Server SHALL 클라이언트와 양방향 실시간 연결을 유지한다
2. WHEN 사용자가 메시지를 전송하면, THE WebSocket_Server SHALL 즉시 메시지를 수신하고 처리한다
3. WHEN AI 응답이 생성되면, THE WebSocket_Server SHALL 실시간으로 클라이언트에 전송한다
4. THE WebSocket_Server SHALL 스트리밍 방식으로 AI 응답을 전송하여 타이핑 효과를 제공한다
5. IF 연결이 끊어지면, THEN THE WebSocket_Server SHALL 재연결을 지원하고 대화 상태를 복원한다
6. THE WebSocket_Server SHALL 동시 다중 사용자 연결을 처리한다

### Requirement 8: 확장 가능한 아키텍처

**User Story:** As a 개발자, I want 시스템에 새로운 기능을 쉽게 추가할 수 있기를, so that 향후 요구사항 변화에 유연하게 대응할 수 있다

#### Acceptance Criteria

1. THE Chat_System SHALL MCP(Model Context Protocol) 서버를 통합할 수 있는 인터페이스를 제공한다
2. THE Chat_System SHALL 멀티 에이전트 아키텍처를 지원하여 독립적인 에이전트를 추가할 수 있다
3. THE Chat_System SHALL 각 컴포넌트 간 느슨한 결합을 유지하여 독립적인 개발과 배포를 가능하게 한다
4. THE Chat_System SHALL 플러그인 방식으로 새로운 기능 모듈을 추가할 수 있다
5. THE Chat_System SHALL 이벤트 기반 아키텍처를 사용하여 컴포넌트 간 통신을 처리한다
6. THE Chat_System SHALL API 버전 관리를 지원하여 하위 호환성을 유지한다

### Requirement 9: 자율적 행동 결정 시스템

**User Story:** As a AI 캐릭터, I want 상황에 맞게 자율적으로 행동을 결정하기를, so that 사용자에게 더 자연스럽고 생동감 있는 대화 경험을 제공할 수 있다

#### Acceptance Criteria

1. THE Chat_System SHALL 멀티 에이전트를 통해 주기적으로 사용자 상태와 대화 맥락을 수집하고 분석한다
2. WHEN 분석이 완료되면, THE Chat_System SHALL "말 걸기", "침묵 유지", "대화에 반응" 중 적절한 행동을 결정한다
3. THE Chat_System SHALL 사용자의 현재 활동 상태, 마지막 대화 시간, 대화 맥락을 종합적으로 고려하여 행동을 판단한다
4. WHEN "말 걸기" 행동이 결정되면, THE Chat_System SHALL 자연스러운 타이밍에 대화를 시작한다
5. THE Chat_System SHALL 시간대, 사용자 선호도, 과거 반응 패턴을 학습하여 행동 결정의 정확도를 개선한다
6. THE Chat_System SHALL 행동 결정 이력을 저장하여 패턴을 분석하고 최적화한다
7. IF 사용자가 바쁜 상태로 판단되면, THEN THE Chat_System SHALL "침묵 유지" 행동을 선택한다

### Requirement 10: 데이터 보안 및 개인정보 보호

**User Story:** As a 사용자, I want 내 대화 내용이 안전하게 보호되기를, so that 개인정보 유출 걱정 없이 대화할 수 있다

#### Acceptance Criteria

1. THE Chat_System SHALL 모든 대화 데이터를 암호화하여 PostgreSQL에 저장한다
2. THE WebSocket_Server SHALL TLS/SSL을 사용하여 통신을 암호화한다
3. THE Chat_System SHALL 사용자별로 대화 데이터를 격리하여 저장한다
4. THE Chat_System SHALL 사용자 인증 및 권한 관리를 구현한다
5. THE Chat_System SHALL 개인정보를 LLM API 전송 전에 마스킹하거나 제거한다
6. THE Chat_System SHALL 데이터 보관 기간 정책을 지원하고 만료된 데이터를 자동 삭제한다

### Requirement 11: 기술 스택 및 시스템 제약사항

**User Story:** As a 개발자, I want 시스템이 명확한 기술 스택과 제약사항 내에서 구현되기를, so that 일관된 개발 환경과 성능 기준을 유지할 수 있다

#### Acceptance Criteria

1. THE Chat_System SHALL Python 프로그래밍 언어로 구현된다
2. THE WebSocket_Server SHALL FastAPI 프레임워크를 사용하여 비동기 처리와 WebSocket 통신을 구현한다
3. THE Chat_System SHALL LangGraph 프레임워크를 사용하여 멀티 에이전트 오케스트레이션을 구현한다
4. THE LLM_Adapter SHALL LangChain을 사용하여 LLM 추상화 계층을 구현한다
5. THE Memory_System SHALL PostgreSQL 데이터베이스를 사용하여 대화 데이터를 저장한다
6. THE Memory_System SHALL pgvector 확장 또는 별도 벡터 데이터베이스를 사용하여 벡터 검색을 구현한다
7. THE Chat_System SHALL 200,000 토큰 이하의 Context_Window 크기로 LLM 요청을 제한한다
8. THE Chat_System SHALL AWS 클라우드 환경에 배포 가능하도록 구현된다
9. WHEN LLM 요청이 생성되면, THE Chat_System SHALL 총 토큰 수가 200,000을 초과하지 않도록 컨텍스트를 관리한다
10. IF 컨텍스트가 200,000 토큰을 초과하면, THEN THE Chat_System SHALL 오래된 대화 내용을 요약하거나 제거하여 토큰 수를 조정한다

