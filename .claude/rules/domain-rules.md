# 도메인 규칙

## Memory 관련

- 모든 Memory Object 필수 필드: `importance_score`, `memory_strength`, `access_count`, `created_at`, `last_access_time`
- Observation은 원본 메시지와 **별도** 저장 (검색 최적화 목적)
- Reflection은 "요약"이 아닌 "상위 의미 추론" — 사용자 패턴/선호/목표 추론
- Importance Score는 LLM이 자동 평가 → 초기 Memory Strength로 사용
- Reflection 트리거: 최근 Observation들의 `importance_score` 누적 합 ≥ 임계값
- User Portrait 업데이트: 새 Reflection 일정 개수 이상 축적 시
- Memory Suppression: 삭제 대신 `disclosure_weight` 낮춰 억제, Retrieval Score에 `base_score * disclosure_weight` 적용
- 컨텍스트 윈도우 초과 시: `Memory_Strength` 낮은 기억부터 제거, 최근 5개 메시지는 유지

## 대화 정책 (Planning Agent 내부 적용)

- 연속 질문 최대 1회 (`max_consecutive_questions=1`)
- Short Reaction은 강한 신호(감정 공유, 놀람, 강한 동의)시에만 조건부 포함
- Anti-Sycophancy: 감정 공감(`emotion_validate=True`)과 사실 동조는 별개 — Loaded Premise 감지 시 부드럽게 수정
- Repair 순서: acknowledge → restate → correct → continue
- Formality는 캐릭터 system prompt에서 고정, 감정 강도 ≥ `formality_deviation_threshold`(0.7)시에만 일시적 이탈
- `ConversationPolicy`는 frozen dataclass로 LangGraph 초기화 시 주입 — 별도 노드로 만들지 않음

## 보안

- LLM API 전송 전 PII 마스킹 필수
- 사용자별 DB 쿼리 격리 (`person_id` 필터 필수)
- WebSocket TLS/SSL 적용
