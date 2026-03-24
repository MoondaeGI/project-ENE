# Implementation Plan: AI Character Chat System

## Overview

Bottom-up 구현 순서: 기반 인프라(DB, LLM 추상화) → 핵심 메모리 시스템 → 에이전트 컴포넌트 → 메인 워크플로우 → WebSocket 통합

- `*` 표시: 선택적 테스트 태스크 (MVP에서 skip 가능)
- `[-]`: 부분 완료, `[x]`: 완료, `[ ]`: 미완료

## Tasks

- [-] 1. Set up project infrastructure and directory structure
  - [x] 1.0 기본 디렉터리 구조 생성 및 파일 마이그레이션 (완료)
  - [-] 1.1 Set up Alembic migration system
    - Run `alembic init src/database/migrations/`
    - Configure `env.py` to use async engine
    - Create initial migration for all tables with HNSW vector indexes
    - _Requirements: 11.5, 11.6_
  - [ ] 1.2 Create utility scripts and config files
    - `scripts/setup_db.py` (pgvector 확장 초기화 + 마이그레이션)
    - `scripts/seed_data.py` (초기 캐릭터 데이터)
    - `config/development.yaml`, `config/production.yaml`, `config/test.yaml`
    - `tests/conftest.py` (shared fixtures: async DB session, test client)
    - _Requirements: 11.5, 11.8_
  - [ ]* 1.3 Write unit tests for database connection and schema validation

- [ ] 2. Implement LLM Abstraction Layer
  - [ ] 2.1 Create LLMProvider protocol interface
    - `generate()`, `stream()`, `get_token_count()` 메서드
    - 표준 request/response 데이터 구조
    - _Requirements: 1.1, 1.6, 1.7, 11.4_
  - [ ] 2.2 Implement LLMAdapter with plugin registration system
    - provider registry (Dict[str, LLMProvider])
    - `register_provider()`, `set_default_provider()`
    - 에러 처리 및 표준 에러 응답
    - _Requirements: 1.1, 1.4, 1.5, 1.8, 1.9_
  - [ ] 2.3 Implement OpenAI provider
    - _Requirements: 1.2, 1.6, 1.7_
  - [ ] 2.4 (추후) Implement additional providers (Anthropic, Google, Ollama, LM Studio)
    - _Requirements: 1.3, 1.6, 1.7_
  - [ ]* 2.5 Write unit tests for LLM Adapter

- [ ] 3. Checkpoint - DB + LLM 테스트 통과 확인

- [ ] 4. Implement Memory Stream core components
  - [ ] 4.1 Create Memory data models and base classes
    - `Memory` dataclass, `MemoryType` enum
    - Message, Observation, Episode, Reflection dataclasses
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  - [ ] 4.2 Implement embedding service
    - `EmbeddingService.embed()`, 캐싱 적용
    - _Requirements: 3.7, 11.4_
  - [ ] 4.3 Implement MemoryStream class
    - `add_message()`, `create_observation()`, `get_recent_memories()`, `update_access_time()`
    - _Requirements: 3.1, 3.2, 3.3, 3.8, 3.11_
  - [ ]* 4.4 Write unit tests for Memory Stream

- [ ] 5. Implement Memory Evolution Engine
  - [ ] 5.1 Forgetting curve logic
    - `calculate_memory_strength()`, `apply_forgetting_curve()`, `reinforce_memory()`, `decay_unused_memories()`
    - 공식: `Memory_Strength(t) = Initial_Strength * e^(-decay_rate * t) + Σ(reinforcement)`
    - _Requirements: 3.7.4~3.7.12_
  - [ ] 5.2 Memory access tracking
    - `record_access()`, `access_count` 업데이트
  - [ ]* 5.3 Write unit tests

- [ ] 6. Implement advanced Retrieval Engine
  - [ ] 6.1 RetrievalEngine with multi-factor scoring
    - `calculate_retrieval_score()`: Recency + Memory_Strength + Relevance
    - Disclosure 필터 (`base_score * disclosure_weight`)
    - _Requirements: 3.5~3.8, 3.7.11_
  - [ ] 6.2 RetrievalConfig and weight management
    - `RetrievalConfig(top_k, weights, memory_types, time_range)`
  - [ ]* 6.3 Write unit tests

- [ ] 7. Checkpoint - Memory system 테스트 통과 확인

- [ ] 8. Implement Reflection system
  - [ ] 8.1 ReflectionGenerator
    - `should_generate_reflection()`: importance 누적 합 ≥ 임계값 확인
    - `generate_reflection()`: LLM으로 상위 의미 추론
    - `store_reflection()`: source tracking 포함 저장
    - _Requirements: 3.5.1~3.5.7_
  - [ ]* 8.2 Write unit tests

- [ ] 9. Implement Episode management
  - [ ] 9.1 EpisodeManager
    - `create_episode()`: purpose, turning_point, conclusion, emotion_changes 포함
    - `update_episode_status()`: ONGOING / COMPLETED
    - _Requirements: 3.4, 3.9, 3.10, 3.12_
  - [ ]* 9.2 Write unit tests

- [ ] 10. Implement User Portrait system
  - [ ] 10.1 UserPortraitManager
    - `build_portrait_from_reflections()`, `update_portrait()`, `get_portrait_confidence()`
    - `personality_traits`, `communication_style`, `interests`, `preferences`, `confidence_score`
    - _Requirements: 3.7.1~3.7.13_
  - [ ]* 10.2 Write unit tests

- [ ] 11. Checkpoint - Reflection, Episode, Portrait 테스트 통과 확인

- [ ] 12. Implement Emotion Agent
  - [ ] 12.1 EmotionAgent
    - `analyze_user_emotion()`, `update_character_emotion()`, `detect_repair_trigger()`
    - 6차원 감정: joy, sadness, anger, surprise, fear, disgust
    - _Requirements: 5.1~5.5_
  - [ ] 12.2 EmotionOrchestrator (LangGraph subgraph)
    - 노드: analyze_user_emotion → update_ai_emotion → save_history → check_extreme_emotion → (조건부) handle_extreme_emotion
    - _Requirements: 5.1~5.6_
  - [ ]* 12.3 Write unit tests

- [ ] 13. Implement Planning Agent
  - [ ] 13.1 PlanningAgent
    - `plan()`, `decide_clarification()`, `check_sycophancy()`
    - ConversationPolicy 주입받아 내부 규칙 적용
    - _Requirements: 4.5.1~4.5.9_
  - [ ]* 13.2 Write unit tests

- [ ] 14. Implement Conversation Policy
  - [ ] 14.1 ConversationPolicy (frozen dataclass)
    - `max_consecutive_questions=1`, `clarification_threshold=0.4`
    - `repair_trigger_emotion_delta=0.3`, `formality_deviation_threshold=0.7`
    - _Requirements: 4.1~4.10_

- [ ] 15. Implement Topic Recommender
  - [ ] 15.1 TopicRecommender
    - `extract_interests()`, `recommend_topics()`, `update_interest_profile()`
    - _Requirements: 6.1, 6.3~6.5_
  - [ ]* 15.2 Write unit tests

- [ ] 16. Checkpoint - Agent component 테스트 통과 확인

- [ ] 17. Implement LangGraph Chain Components
  - [ ] 17.1 AutonomousBehaviorChain: 'respond' / 'silence' / 'initiate' 결정
  - [ ] 17.2 MemoryRetrievalChain: 기억 검색 + 접근 시간 업데이트
  - [ ] 17.3 DialoguePlanningChain: 대화 목표 + 응답 의도 설정
  - [ ] 17.4 ConversationPolicyChain: 정책 규칙 검증
  - [ ] 17.5 MessageGenerationChain: `ainvoke()` + `astream()`, Portrait 기반 개인화
  - [ ]* 17.6 Write unit tests

- [ ] 18. Implement Memory Save Orchestrator (LangGraph subgraph)
  - save_message → create_observation → calculate_importance → check_reflection_trigger → (조건부) generate_reflection → update_user_portrait
  - _Requirements: 3.1, 3.2, 3.5.3, 3.7.3_

- [ ] 19. Implement Main Workflow (LangGraph StateGraph)
  - [ ] 19.1 MainConversationChain: 전체 노드 연결 + 조건부 엣지
  - [ ] 19.2 `ainvoke()` + `astream()` 구현
  - [ ]* 19.3 Write integration tests

- [ ] 20. Checkpoint - Workflow integration 테스트 통과 확인

- [ ] 21. Implement Character Persona management
  - CharacterPersona: name, personality, speaking_style, base_formality, background, system_prompt

- [ ] 22. Implement WebSocket Server
  - [ ] 22.1 FastAPI WebSocket: connect, disconnect, receive_message, stream_response, 다중 세션
  - [ ] 22.2 재연결 + 상태 복원 (exponential backoff + 메시지 큐)
  - [ ]* 22.3 Integration tests

- [ ] 23. Implement security and privacy features
  - DB 암호화, TLS/SSL, 사용자 인증, PII 마스킹, 데이터 보관 정책

- [ ] 24. Implement context window management
  - 200,000 토큰 초과 시 Memory_Strength 낮은 기억부터 제거, 최근 5개 메시지 유지

- [ ] 25. Background jobs for memory evolution
  - 매일 자정: decay 적용, Portrait 업데이트, 약한 기억 아카이브

- [ ] 26. Tag-based keyword indexing
  - `extract_keywords()`, tag 테이블 연동, 벡터 검색 실패 시 fallback

- [ ] 27. Wire all components + main application entry point
  - FastAPI 앱 초기화, DI, health check, API 버전 관리

- [ ] 28. Final checkpoint - 전체 테스트 통과 확인