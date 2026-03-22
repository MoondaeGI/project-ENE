# Check Requirements

구현 전 요구사항 및 설계 명세를 확인합니다.

## 사용법

```
/check-requirements <요구사항 번호 또는 컴포넌트명>
예: /check-requirements 3        # Requirement 3 전체
예: /check-requirements memory   # 메모리 관련 요구사항
예: /check-requirements llm      # LLM 추상화 요구사항
```

## 요구사항 → 설계 매핑

| Requirement | 내용 | 관련 design |
|-------------|------|------------|
| Req 1 | LLM 추상화 계층 (Plugin 방식) | `design/05_llm_adapter.md` |
| Req 2 | 캐릭터 페르소나 설정 | `design/02_agents.md` |
| Req 3 | 대화 기억 시스템 (Memory Stream & Retrieval) | `design/03_memory_system.md` |
| Req 3.5 | Reflection 시스템 (상위 의미 추론) | `design/03_memory_system.md` |
| Req 3.7 | User Portrait & Memory Evolution | `design/03_memory_system.md` |
| Req 4 | 자연스러운 대화 정책 | `design/02_agents.md` |
| Req 4.5 | Planning & Dialogue Intention | `design/02_agents.md` |
| Req 5 | 감정 인식 및 관리 | `design/02_agents.md` |
| Req 6 | 개인화된 주제 추천 | `design/02_agents.md` |
| Req 7 | WebSocket 실시간 통신 | `design/01_workflow.md` |
| Req 8 | 확장 가능한 아키텍처 | `design/00_overview.md` |
| Req 9 | 자율적 행동 결정 | `design/01_workflow.md` |
| Req 10 | 데이터 보안 및 개인정보 보호 | `design/07_error_handling.md` |
| Req 11 | 기술 스택 및 제약사항 | `design/00_overview.md` |

## 주요 Acceptance Criteria 요약

### Memory System (Req 3, 3.5, 3.7)
- Observation: `creation_time`, `last_access_time`, `importance_score` 필수
- Retrieval_Score = Recency + Memory_Strength + Relevance 가중합
- Reflection 트리거: importance_score 누적 합 ≥ 임계값
- Memory Suppression: `disclosure_weight` 낮춰 억제 (삭제 X)
- Emotional Snapshot: Observation 저장 시 감정 상태 스냅샷 함께 저장

### Conversation Policy (Req 4)
- 연속 질문 최대 1회 (`max_consecutive_questions=1`)
- Clarification: `ambiguity_score * harm_score > threshold` 공식
- Anti-Sycophancy: 감정 공감 ≠ 사실 동조
- Repair: acknowledge → restate → correct → continue

### Technical Constraints (Req 11)
- Context Window: 200,000 토큰 초과 시 Memory_Strength 낮은 기억부터 제거
- 비동기 처리: FastAPI + async/await 전체 적용
- 플러그인: 기존 코드 수정 없이 LLM Provider 추가 가능

## 확인 방법

```bash
# 요구사항 전체 보기
cat .kiro/specs/ai-character-chat-system/requirements.md

# 특정 requirement 보기 (grep)
grep -A 20 "Requirement 3:" .kiro/specs/ai-character-chat-system/requirements.md
```

---

확인 대상: $ARGUMENTS
