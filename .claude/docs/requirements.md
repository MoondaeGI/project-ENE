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
- **Assumed_Referents**: 현재 대화에서 AI가 공유된 것으로 가정 중인 지시 대상
- **Clarification_Decision**: 모호한 발화에 대해 질문할지 가정하고 진행할지 결정하는 정책 (ambiguity_score * harm_score > threshold)
- **Repair_Policy**: 오해, 감정 불일치, 기억 오류 발생 시 대화를 복구하는 정책 (acknowledge → restate → correct → continue)
- **Repair_Mode**: 복구 강도 수준 — none / soft / explicit
- **Anti_Sycophancy**: 사용자의 감정은 공감하되 사실 판단은 자동 동조하지 않는 원칙
- **Loaded_Premise**: 사실로 단정된 전제가 포함된 발화
- **Emotional_Snapshot**: Observation/Episode 저장 시 함께 기록되는 감정 상태 스냅샷
- **Emotional_Valence**: 감정의 긍정/부정 강도 (-1.0 부정 ~ 1.0 긍정)
- **Emotional_Alignment**: 사용자-AI 감정 일치도 (0.0~1.0)
- **Disclosure_Weight**: 기억의 출현도 가중치 — Retrieval Score에 곱해져 억제된 기억이 자연스럽게 하위권으로 밀림
- **Memory_Suppression**: 삭제 대신 disclosure_weight를 낮춰 기억의 출현 빈도를 억제하는 메커니즘
- **Emotion_State**: 기쁨, 슬픔, 분노 등 다차원 감정 수치

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

1. THE Memory_System SHALL Reflection을 "요약"이 아닌 "상위 의미 추론"으로 생성한다
2. THE Memory_System SHALL Reflection을 통해 사용자 패턴, 선호도, 목표, 관계를 추론한다
3. WHEN Importance_Score의 누적 합이 임계값에 도달하면, THE Memory_System SHALL 자동으로 Reflection을 생성한다
4. THE Memory_System SHALL Reflection 자체도 Observation과 동일하게 검색 대상으로 포함한다
5. THE Memory_System SHALL 각 Reflection에 Importance_Score를 할당한다
6. THE Memory_System SHALL Reflection을 Memory_Stream에 저장하여 시간순 기억 흐름에 포함한다
7. WHEN Reflection이 생성되면, THE Memory_System SHALL 해당 Reflection의 근거가 된 Observation들을 참조로 기록한다
8. Reflection 예시: "사용자는 구조 설계를 선호한다", "사용자는 실무 적용 가능성을 중요하게 본다"

### Requirement 3.7: User Portrait & Memory Evolution

**User Portrait**
1. THE Memory_System SHALL 사용자별 User_Portrait를 생성하고 관리한다
2. THE User_Portrait SHALL 성격 특성, 의사소통 스타일, 관심사, 선호도를 포함한다
3. WHEN Reflection이 생성되면, THE Memory_System SHALL User_Portrait를 업데이트한다
4. THE Chat_System SHALL User_Portrait를 응답 생성 시 참고하여 개인화된 대화를 제공한다
5. THE User_Portrait SHALL 신뢰도 점수(confidence_score)를 포함한다
6. 계층적 사용자 이해: Level 1 (사실 기억 - Observation), Level 2 (패턴 추론 - Reflection), Level 3 (사용자 프로필 - Portrait)

**Memory Evolution**
7. THE Memory_System SHALL 시간 경과에 따라 기억의 강도를 조정한다 (망각 곡선 기반)
8. WHEN 기억이 반복적으로 접근되면, THE Memory_System SHALL 해당 기억의 Memory_Strength를 증가시킨다
9. WHEN 기억이 오래 접근되지 않으면, THE Memory_System SHALL 해당 기억의 강도를 감소시킨다
10. THE Memory_System SHALL Memory_Strength를 계산할 때 Importance_Score와 시간 감쇠를 결합한다
11. THE Memory_System SHALL Forgetting_Curve를 적용하여 오래된 기억의 검색 우선순위를 낮춘다

**Memory Suppression**
12. WHEN 사용자가 특정 기억을 꺼내지 말라고 요청하면, THE Memory_System SHALL 해당 기억을 삭제하지 않고 Disclosure_Weight를 대폭 낮춘다
13. Retrieval Score 계산 시 `base_score * disclosure_weight` 적용
14. WHEN 사용자가 억제된 기억의 주제를 직접 언급하면, THE Memory_System SHALL 해당 기억을 일시적으로 재활성화한다
15. THE Memory_System SHALL suppression_reason을 기록하여 억제 이유를 추적한다

**Emotional Snapshot**
16. WHEN Observation이 저장되면, THE Memory_System SHALL 그 시점의 Emotional_Snapshot을 함께 저장한다
17. THE Emotional_Snapshot SHALL user_emotion_snapshot, ai_emotion_snapshot, emotional_valence, emotional_arousal, emotional_alignment를 포함한다
18. WHEN Episode가 완료되면, emotional_valence 평균을 avg_emotional_valence로 저장한다

### Requirement 4: 자연스러운 대화 정책

**질문 제한 및 Clarification**
1. 연속된 질문의 개수를 제한 (최대 연속 1회)
2. WHEN 모호한 발화가 감지되면, `ambiguity_score * harm_score > threshold` 공식으로 질문 여부 결정
3. WHEN 오해 비용이 낮고 지배적 해석이 있으면, 가정하고 진행하며 assumed_referents에 기록
4. WHEN 질문이 필요하면, 한 번에 하나의 질문만 한다

**응답 구조**
5. short reaction은 강한 신호(감정 공유, 급격한 주제 전환)가 있을 때만 조건부 포함
6. 단순 정보 질문 또는 명확한 작업 요청 시 short reaction 없이 바로 본론 응답
7. 직전 턴에 이미 short reaction을 사용했으면, 다음 턴에는 포함하지 않는다

**Grounding & Common Ground**
8. 대화 중 Common_Ground_State를 유지하여 assumed_referents, open_ambiguities, user_visible_commitments를 추적
9. WHEN assumed_referent가 사용자에게 정정되면, 즉시 Common_Ground_State를 업데이트

**Repair Policy**
10. WHEN 오해, 감정 불일치, 기억 오류, 사실 오류가 감지되면, Repair_Policy를 적용
11. repair 순서: acknowledge → restate → correct → continue
12. repair_mode: none / soft / explicit 중 심각도에 따라 결정
13. 기억 mismatch로 repair 발생 시, 해당 기억의 memory_strength를 하향 조정

**Anti-Sycophancy**
14. 사용자의 감정은 공감하되 사실 판단은 자동으로 동조하지 않는다 (emotion_validate=True, premise_accept=별도 판단)
15. Loaded_Premise 감지 시 전제를 사실로 수용하지 않고 부드럽게 재구성
16. Loaded_Premise를 사실로 기억에 저장하지 않는다

**스타일 적응**
17. 사용자의 대화 스타일을 EMA 기반으로 학습하되 캐릭터 고유 스타일 유지 (bounded adaptation)
18. formality는 캐릭터 system prompt에서 기본값 고정, AI 감정 강도가 임계값 초과 시만 일시적 이탈

**프로액티브 대화**
19. 사용자가 일정 시간 응답하지 않으면, 내재적 동기 점수 평가 후 먼저 대화 시작 가능
20. "정보 제공자"가 아닌 "생각을 함께 이어가는 동반자"로서 대화

### Requirement 4.5: Planning & Dialogue Intention

1. 대화 목표를 설정하고 Dialogue_Intention을 통해 응답 의도를 계획: 설명, 설계, 위로, 의사결정 보조 등
2. 사용자의 장기 작업 흐름을 이해하고 이전 대화와 연결
3. 대화 종료 후 남길 상태를 관리: 미해결 질문, 다음 논의 주제, 사용자 감정 상태 등

### Requirement 5: 감정 인식 및 관리 시스템

1. THE Emotion_Agent SHALL 다차원 감정 수치(기쁨, 슬픔, 분노, 놀람, 두려움, 혐오)를 관리한다
2. WHEN 사용자 메시지가 수신되면, 사용자의 감정 상태를 분석하여 수치화한다
3. AI 캐릭터의 현재 감정 상태를 유지하고 대화에 따라 업데이트한다
4. WHEN AI가 응답을 생성할 때, 현재 감정 상태를 반영하여 응답을 생성한다
5. 감정 변화 이력을 저장하여 감정의 연속성을 유지한다
6. 감정 수치에 따라 응답의 톤, 어휘 선택, 문장 구조를 조정한다

### Requirement 6: 개인화된 주제 추천

1. 대화 내용을 분석하여 사용자의 관심사를 추출한다
2. THE Topic_Recommender SHALL AWS 클라우드 환경에서 백그라운드로 실행된다
3. WHEN 새로운 관심 주제가 발견되면, Memory_System에 주제 정보를 업데이트한다
4. 사용자의 반응을 학습하여 주제 추천 정확도를 개선한다

### Requirement 7: WebSocket 실시간 통신

1. THE WebSocket_Server SHALL 클라이언트와 양방향 실시간 연결을 유지한다
2. 스트리밍 방식으로 AI 응답을 전송하여 타이핑 효과를 제공한다
3. IF 연결이 끊어지면, THEN 재연결을 지원하고 대화 상태를 복원한다
4. THE WebSocket_Server SHALL 동시 다중 사용자 연결을 처리한다

### Requirement 9: 자율적 행동 결정 시스템

1. 멀티 에이전트를 통해 주기적으로 사용자 상태와 대화 맥락을 수집하고 분석한다
2. WHEN 분석이 완료되면, "말 걸기", "침묵 유지", "대화에 반응" 중 적절한 행동을 결정한다
3. 사용자의 현재 활동 상태, 마지막 대화 시간, 대화 맥락을 종합적으로 고려한다
4. IF 사용자가 바쁜 상태로 판단되면, THEN "침묵 유지" 행동을 선택한다

### Requirement 10: 데이터 보안 및 개인정보 보호

1. 모든 대화 데이터를 암호화하여 PostgreSQL에 저장 (at-rest 암호화)
2. THE WebSocket_Server SHALL TLS/SSL을 사용하여 통신을 암호화한다
3. 사용자별로 대화 데이터를 격리하여 저장한다
4. 사용자 인증 및 권한 관리를 구현한다
5. 개인정보를 LLM API 전송 전에 마스킹하거나 제거한다
6. 데이터 보관 기간 정책을 지원하고 만료된 데이터를 자동 삭제한다

### Requirement 11: 기술 스택 및 시스템 제약사항

1. Python 3.11+, FastAPI (비동기/WebSocket), LangGraph (멀티 에이전트), LangChain (LLM 추상화)
2. PostgreSQL + pgvector (벡터 검색)
3. Context Window: 200,000 토큰 이하로 LLM 요청 제한
4. IF 컨텍스트가 200,000 토큰을 초과하면, 오래된 대화 내용을 요약하거나 제거하여 토큰 수를 조정한다
5. AWS 클라우드 환경에 배포 가능하도록 구현한다
