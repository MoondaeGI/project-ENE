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

## DTO 규칙

레이어 간 데이터 이동은 반드시 해당 레이어의 DTO를 사용한다.

| 이동 구간 | DTO 위치 |
| --- | --- |
| HTTP 요청/응답 (client ↔ controller) | `api/dto/request/`, `api/dto/response/` |
| Controller ↔ Service | `services/dto/` |
| Service ↔ DAO (Repository) | `database/dto/` |

- ORM 모델(`database/models.py`)을 서비스 레이어 밖으로 노출 금지
- 각 레이어는 인접 레이어의 DTO만 참조 (건너뛰기 금지)

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

## 민감 데이터 규칙

- API 키, 비밀번호, 시크릿 등 민감한 값은 **절대 하드코딩 금지**
- 모든 민감 값은 `.env`에서 관리
- `.env`에 값을 추가하거나 수정할 때마다 `.env.example`도 동일하게 반영 (값은 플레이스홀더로)
- 민감한 문자열 생성·추가가 필요하면 구현 전 반드시 사용자에게 먼저 요청

```python
# ❌ 금지
api_key = "sk-abc123..."

# ✅ 올바른 방법
api_key = settings.llm.openai_api_key  # .env에서 로드
```
