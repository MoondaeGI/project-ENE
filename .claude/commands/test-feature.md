# Test Feature

구현한 함수 또는 기능의 테스트 코드를 작성하고 실행합니다.

## 사용법

```
/test-feature <파일경로 또는 함수명>
예: /test-feature services/memory_service.py
예: /test-feature MemoryRetrievalService.retrieve
예: /test-feature LLMAdapter
```

## 테스트 작성 절차

### 1. 대상 코드 파악

- 지정한 파일 또는 함수를 읽어 시그니처, 의존성, 반환값 파악
- `design/08_testing.md` 에서 해당 컴포넌트의 테스트 전략 확인

### 2. 테스트 위치 결정

| 대상 유형 | 테스트 경로 |
|-----------|------------|
| 순수 로직 / 유틸리티 | `tests/unit/` |
| Service (DB 호출 포함) | `tests/integration/` |
| LangGraph 워크플로우 | `tests/integration/` |
| API 엔드포인트 | `tests/integration/` |
| E2E 시나리오 | `tests/e2e/` |

### 3. 테스트 코드 작성 원칙

- **DB 테스트**: Mock 금지 — 실제 DB 연결 사용 (testcontainers 또는 test DB)
- **LLM 테스트**: 단위 테스트에서는 LLM 응답 fixture로 Mock 허용
- **비동기**: `pytest-asyncio` + `@pytest.mark.asyncio` 필수
- **픽스처**: `tests/conftest.py` 의 공통 픽스처 우선 활용

```python
# 테스트 파일 기본 구조
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_기능명_정상케이스():
    # Arrange
    ...
    # Act
    result = await target_function(...)
    # Assert
    assert result == expected

@pytest.mark.asyncio
async def test_기능명_예외케이스():
    ...
```

### 4. 필수 커버리지 체크리스트

- [ ] 정상 동작 (happy path)
- [ ] 경계값 (빈 입력, 최대값)
- [ ] 예외 처리 (DB 실패 → fallback, LLM 실패 → retry/provider 전환)
- [ ] Memory 관련이면: `importance_score`, `memory_strength`, `disclosure_weight` 검증

### 5. 테스트 실행

```bash
# 특정 파일만
python -m pytest tests/unit/test_<파일명>.py -v

# 특정 함수만
python -m pytest tests/unit/test_<파일명>.py::test_함수명 -v

# 커버리지 포함
python -m pytest tests/unit/ --cov=src --cov-report=term-missing -v

# 통합 테스트
python -m pytest tests/integration/ -v --timeout=30
```

### 6. 성능 목표 확인 (`design/08_testing.md`)

- Memory Retrieval: p95 < 200ms
- LLM 응답: p95 < 3s
- WebSocket 메시지: p99 < 100ms

---

테스트 대상: $ARGUMENTS
