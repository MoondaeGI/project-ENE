# Requirements — 대화 정책·감정·보안·인프라

[← requirements.md](requirements.md) 에서 이어지는 문서입니다.

## Requirement 3.7: User Portrait & Memory Evolution

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

## Requirement 4: 자연스러운 대화 정책

**질문 제한 및 Clarification**

1. 연속된 질문의 개수를 제한 (최대 연속 1회)
2. WHEN 모호한 발화가 감지되면, `ambiguity_score * harm_score > threshold` 공식으로 질문 여부 결정
3. WHEN 오해 비용이 낮고 지배적 해석이 있으면, 가정하고 진행하며 assumed_referents에 기록
4. WHEN 질문이 필요하면, 한 번에 하나의 질문만 한다

**응답 구조**

5. short reaction은 강한 신호(감정 공유, 급격한 주제 전환)가 있을 때만 조건부 포함
6. 단순 정보 질문 또는 명확한 작업 요청 시 short reaction 없이 바로 본론 응답
7. 직전 턴에 이미 short reaction을 사용했으면, 다음 턴에는 포함하지 않는다

**Repair Policy**

8. WHEN 오해, 감정 불일치, 기억 오류, 사실 오류가 감지되면, Repair_Policy를 적용
9. repair 순서: acknowledge → restate → correct → continue
10. repair_mode: none / soft / explicit 중 심각도에 따라 결정
11. 기억 mismatch로 repair 발생 시, 해당 기억의 memory_strength를 하향 조정

**Anti-Sycophancy**

12. 사용자의 감정은 공감하되 사실 판단은 자동으로 동조하지 않는다 (emotion_validate=True, premise_accept=별도 판단)
13. Loaded_Premise 감지 시 전제를 사실로 수용하지 않고 부드럽게 재구성
14. Loaded_Premise를 사실로 기억에 저장하지 않는다

## Requirement 4.5: Planning & Dialogue Intention

1. 대화 목표를 설정하고 Dialogue_Intention을 통해 응답 의도를 계획: 설명, 설계, 위로, 의사결정 보조 등
2. 사용자의 장기 작업 흐름을 이해하고 이전 대화와 연결
3. 대화 종료 후 남길 상태를 관리: 미해결 질문, 다음 논의 주제, 사용자 감정 상태 등

## Requirement 5: 감정 인식 및 관리 시스템

1. THE Emotion_Agent SHALL 다차원 감정 수치(기쁨, 슬픔, 분노, 놀람, 두려움, 혐오)를 관리한다
2. WHEN 사용자 메시지가 수신되면, 사용자의 감정 상태를 분석하여 수치화한다
3. AI 캐릭터의 현재 감정 상태를 유지하고 대화에 따라 업데이트한다
4. WHEN AI가 응답을 생성할 때, 현재 감정 상태를 반영하여 응답을 생성한다
5. 감정 변화 이력을 저장하여 감정의 연속성을 유지한다
6. 감정 수치에 따라 응답의 톤, 어휘 선택, 문장 구조를 조정한다

## Requirement 6: 개인화된 주제 추천

1. 대화 내용을 분석하여 사용자의 관심사를 추출한다
2. THE Topic_Recommender SHALL AWS 클라우드 환경에서 백그라운드로 실행된다
3. WHEN 새로운 관심 주제가 발견되면, Memory_System에 주제 정보를 업데이트한다
4. 사용자의 반응을 학습하여 주제 추천 정확도를 개선한다

## Requirement 7: WebSocket 실시간 통신

1. THE WebSocket_Server SHALL 클라이언트와 양방향 실시간 연결을 유지한다
2. 스트리밍 방식으로 AI 응답을 전송하여 타이핑 효과를 제공한다
3. IF 연결이 끊어지면, THEN 재연결을 지원하고 대화 상태를 복원한다
4. THE WebSocket_Server SHALL 동시 다중 사용자 연결을 처리한다

## Requirement 9: 자율적 행동 결정 시스템

1. 멀티 에이전트를 통해 주기적으로 사용자 상태와 대화 맥락을 수집하고 분석한다
2. WHEN 분석이 완료되면, "말 걸기", "침묵 유지", "대화에 반응" 중 적절한 행동을 결정한다
3. 사용자의 현재 활동 상태, 마지막 대화 시간, 대화 맥락을 종합적으로 고려한다
4. IF 사용자가 바쁜 상태로 판단되면, THEN "침묵 유지" 행동을 선택한다

## Requirement 10: 데이터 보안 및 개인정보 보호

1. 모든 대화 데이터를 암호화하여 PostgreSQL에 저장 (at-rest 암호화)
2. THE WebSocket_Server SHALL TLS/SSL을 사용하여 통신을 암호화한다
3. 사용자별로 대화 데이터를 격리하여 저장한다
4. 사용자 인증 및 권한 관리를 구현한다
5. 개인정보를 LLM API 전송 전에 마스킹하거나 제거한다
6. 데이터 보관 기간 정책을 지원하고 만료된 데이터를 자동 삭제한다

## Requirement 11: 기술 스택 및 시스템 제약사항

1. Python 3.11+, FastAPI (비동기/WebSocket), LangGraph (멀티 에이전트), LangChain (LLM 추상화)
2. PostgreSQL + pgvector (벡터 검색)
3. Context Window: 200,000 토큰 이하로 LLM 요청 제한
4. IF 컨텍스트가 200,000 토큰을 초과하면, 오래된 대화 내용을 요약하거나 제거하여 토큰 수를 조정한다
5. AWS 클라우드 환경에 배포 가능하도록 구현한다