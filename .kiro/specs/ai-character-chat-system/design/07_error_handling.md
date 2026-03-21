# Error Handling

## Memory System Errors

### Retrieval Failures
- 벡터 검색 실패 시 키워드 기반 fallback 검색
- 임베딩 생성 실패 시 재시도 (최대 3회)
- 검색 결과 없을 시 기본 컨텍스트 사용

### Memory Evolution Errors
- Memory Strength 계산 실패 시 기본 `importance_score` 사용
- 접근 이력 저장 실패 시 로깅 후 계속 진행
- Portrait 업데이트 실패 시 이전 Portrait 유지

### Database Errors
- 연결 실패 시 재연결 시도 (exponential backoff)
- 트랜잭션 실패 시 롤백 및 재시도
- 벡터 인덱스 오류 시 전체 테이블 스캔 fallback

## LLM Adapter Errors

### Provider Failures
- LLM 호출 실패 시 다른 Provider로 자동 전환
- 타임아웃 시 재시도 (최대 3회)
- Rate limit 초과 시 대기 후 재시도

### Context Window Overflow
- 토큰 수 초과 시 오래된 메시지부터 제거
- Memory Strength 낮은 기억부터 제거
- 최소 컨텍스트 유지 (최근 5개 메시지)

## WebSocket Errors

### Connection Errors
- 연결 끊김 시 자동 재연결 (최대 5회)
- 재연결 시 대화 상태 복원
- 메시지 큐를 사용한 손실 방지

### Message Errors
- 잘못된 형식의 메시지 수신 시 에러 응답
- 메시지 처리 실패 시 사용자에게 알림
- 스트리밍 중단 시 부분 응답 전송
