# 코딩 가이드라인

## Markdown 파일 작성 규칙

- MD 파일은 **200줄을 초과하지 않는다**
- 200줄이 넘을 것 같으면 내용을 분리하고, 원본 파일에서 분리된 파일 경로를 참조한다

## 구현 전 주석 확인 절차

함수를 구현하기 전에 반드시 아래 절차를 따릅니다.

1. **스텁 작성**: 함수 시그니처 + docstring 형태로 역할, 파라미터, 반환값을 먼저 작성합니다.
2. **사용자 확인**: 스텁을 보여주고 구현 방향이 맞는지 확인 요청합니다.
3. **승인 후 구현**: 확인 받은 뒤에만 실제 로직을 작성합니다.

스텁 예시:

```python
async def retrieve_memories(
    owner_id: UUID,
    query: str,
    top_k: int = 10,
) -> list[MemoryBase]:
    """
    벡터 검색 + Retrieval Score 계산으로 관련 기억을 반환합니다.

    Args:
        owner_id: 기억 소유자 ID (participant.id)
        query: 현재 대화 컨텍스트 (임베딩 쿼리로 사용)
        top_k: 반환할 최대 기억 개수

    Returns:
        Retrieval Score 내림차순 정렬된 MemoryBase 리스트
        (score = α*Recency + β*Memory_Strength + γ*Relevance)
    """
    ...
```

## 아키텍처 원칙

- 의존성 방향은 `api → workflow → services → database` 단방향만 허용
- LLM Provider는 `LLMProvider` Protocol 구현 후 `register_provider()`로 등록 — 기존 코드 수정 없이 플러그인 추가
- 에이전트는 독립적으로 동작하고 LangGraph 공유 상태로 협력 (느슨한 결합 유지)
- 이벤트 기반 아키텍처 적용

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

## 비동기 처리

- 모든 DB/LLM 호출은 `async/await` 사용
- WebSocket 스트리밍은 `AsyncIterator[str]`로 처리

## 보안

- LLM API 전송 전 PII 마스킹 필수
- 사용자별 DB 쿼리 격리 (`person_id` 필터 필수)
- WebSocket TLS/SSL 적용

### 민감 데이터 규칙

- API 키, 비밀번호, 시크릿 등 민감한 값은 **절대 하드코딩 금지**
- 모든 민감 값은 `.env`에서 관리
- `.env`에 값을 추가할 때마다 `.env.example`에도 동일한 키를 플레이스홀더로 추가
- 민감한 문자열 생성·추가가 필요하면 구현 전 반드시 사용자에게 먼저 요청

```python
# ❌ 금지
api_key = "sk-abc123..."

# ✅ 올바른 방법
api_key = settings.llm.openai_api_key  # .env에서 로드
```

## 에러 처리

- 벡터 검색 실패 시 tag 기반 keyword 검색으로 fallback
- LLM 호출 실패 시 다른 Provider로 자동 전환, 최대 3회 재시도
- Portrait 업데이트 실패 시 이전 Portrait 유지 (무중단)

## Python 코드 스타일

**Typing**
- 모든 함수에 파라미터와 반환값 타입 명시 필수
- 파라미터 4개 이상이면 dataclass 또는 TypedDict로 묶기
- `Any` 타입 사용 금지

**Docstring**
- 모든 public 함수/클래스에 docstring 필수
- Google 스타일 사용

**API**
- 엔드포인트 구현 전 Pydantic validator 먼저 작성

**예외 처리**
- bare `except:` 금지, 반드시 예외 타입 명시
- 커스텀 예외는 프로젝트 루트 `exceptions.py`에 정의

**함수 설계**
- 함수 하나는 하나의 역할만 (20줄 초과 시 분리 검토)
- 사이드 이펙트 있는 함수는 이름에 동사로 명시 (`save_`, `send_`, `delete_`)

**임포트**
- 상대 임포트 금지, 절대 경로만 사용
- 외부 라이브러리 → 내부 모듈 → 로컬 모듈 순서로 그룹핑

**상수**
- 매직 넘버 금지, 반드시 상수로 정의

