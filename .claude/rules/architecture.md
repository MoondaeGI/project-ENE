# 아키텍처 규칙

## 아키텍처 원칙

- 의존성 방향은 `api → workflow → services → database` 단방향만 허용
- LLM Provider는 `LLMProvider` Protocol 구현 후 `register_provider()`로 등록 — 기존 코드 수정 없이 플러그인 추가
- 에이전트는 독립적으로 동작하고 LangGraph 공유 상태로 협력 (느슨한 결합 유지)
- 이벤트 기반 아키텍처 적용

## 비동기 처리

- 모든 DB/LLM 호출은 `async/await` 사용
- WebSocket 스트리밍은 `AsyncIterator[str]`로 처리

## 에러 처리

- 벡터 검색 실패 시 tag 기반 keyword 검색으로 fallback
- LLM 호출 실패 시 다른 Provider로 자동 전환, 최대 3회 재시도
- Portrait 업데이트 실패 시 이전 Portrait 유지 (무중단)
