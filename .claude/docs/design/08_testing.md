# Testing Strategy

## Unit Testing

### Memory System Tests
- Memory Stream 저장 및 검색
- Observation 생성 로직
- Reflection 생성 조건 (importance 누적 합 ≥ 임계값)
- Episode 관리
- Memory Strength 계산
- User Portrait 생성 및 업데이트

### Agent Tests
- 각 Agent의 독립적인 기능
- Agent 간 상태 전달
- Dialogue Agent 응답 생성 (Formality Shift 포함)
- Emotion Agent 감정 분석 (6차원)
- Planning Agent 목표 설정 및 ConversationPolicy 적용
- Retrieval Agent 검색 정확도

### LLM Adapter Tests
- Provider 등록 및 전환
- 요청/응답 형식 변환
- 에러 처리 및 fallback
- 스트리밍 응답

## Integration Testing

### End-to-End Flow Tests
- 사용자 메시지 → 응답 생성 전체 흐름
- Memory 저장 → 검색 → 응답 반영 흐름
- Reflection 생성 → Portrait 업데이트 흐름
- Memory Evolution 주기적 실행

### Database Integration Tests
- PostgreSQL 연결 및 쿼리
- pgvector 벡터 검색 정확도
- 트랜잭션 및 롤백
- HNSW 인덱스 성능

### WebSocket Integration Tests
- 연결 수립 및 유지
- 메시지 송수신
- 재연결 및 상태 복원
- 동시 다중 사용자

## Performance Targets

| 항목 | 목표 |
|------|------|
| 벡터 검색 응답 시간 | < 100ms |
| LLM 응답 생성 시간 | < 3초 |
| 스트리밍 첫 토큰 시간 | < 500ms |

## Property-Based Testing

### Memory Strength Properties
- **P1**: 시간이 지날수록 Memory Strength는 감소한다
- **P2**: 접근 빈도가 높을수록 Memory Strength는 증가한다
- **P3**: Memory Strength는 항상 0.0 ~ 1.0 범위 내에 있다

### Retrieval Score Properties
- **P4**: Retrieval Score = Recency * α + Memory_Strength * β + Relevance * γ
- **P5**: 최근 접근된 기억은 더 높은 Retrieval Score를 가진다
- **P6**: 관련성 높은 기억은 더 높은 Retrieval Score를 가진다

### User Portrait Properties
- **P7**: Portrait confidence는 Reflection 개수에 비례한다
- **P8**: Portrait는 모든 Reflection을 반영한다
- **P9**: Portrait 업데이트는 이전 Portrait를 기반으로 한다
