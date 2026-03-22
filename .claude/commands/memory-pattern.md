# Memory Pattern Reference

Memory Stream 구현 시 사용하는 핵심 패턴 레퍼런스입니다.

## Retrieval Pattern

```python
# 1. 쿼리 임베딩 생성
query_embedding = await embedding_service.embed(query)

# 2. Retrieval Score 계산 (α=0.3, β=0.4, γ=0.3)
for memory in memories:
    recency = calculate_recency(memory.last_access_time)   # exponential decay
    strength = memory.memory_strength                        # 동적 변화값
    relevance = cosine_similarity(memory.embedding, query_embedding)
    memory.retrieval_score = α*recency + β*strength + γ*relevance

# 3. Disclosure 필터 적용 (disclosure_weight < threshold 제외)
memories = [m for m in memories if m.disclosure_weight >= disclosure_threshold]

# 4. Top-K 선택 및 접근 기록
top_memories = sorted(memories, key=lambda m: m.retrieval_score, reverse=True)[:k]
await update_access_times(top_memories)
await memory_evolution.reinforce_memories(top_memories)
```

## Memory Strength 계산

```python
# 망각 곡선 공식 (Ebbinghaus 기반)
Memory_Strength(t) = Initial_Strength * e^(-decay_rate * t) + Σ(reinforcement_per_access)

# 접근 시 강화
async def reinforce_memory(memory_id: str) -> None:
    memory.memory_strength += reinforcement_delta
    memory.access_count += 1
    memory.last_access_time = datetime.now()
    await record_access_history(memory_id)
```

## Reflection 생성 패턴

```python
# Reflection은 "요약"이 아닌 "상위 의미 추론"
# 예: "사용자는 구조 설계를 선호한다", "사용자는 실무 적용 가능성을 중요하게 본다"

async def check_and_generate_reflection(user_id: str) -> Optional[Reflection]:
    recent_observations = await get_recent_unprocessed_observations(user_id)
    importance_sum = sum(obs.importance_score for obs in recent_observations)

    if importance_sum >= REFLECTION_THRESHOLD:
        # LLM으로 상위 의미 추론
        reflection = await llm.generate_reflection(recent_observations)
        reflection.importance_score = await llm.evaluate_importance(reflection)

        # source 추적 저장
        await store_reflection_with_sources(reflection, recent_observations)

        # User Portrait 업데이트 트리거
        await user_portrait_manager.update_portrait(user_id, reflection)

        return reflection
    return None
```

## Memory Save Subgraph 패턴

```python
# LangGraph 서브그래프 노드 순서
# save_message → create_observation → calculate_importance
#     → check_reflection_trigger
#         → (임계값 도달) generate_reflection → update_user_portrait → END
#         → (미도달) END

class MemorySaveOrchestrator:
    async def save_message(self, state: MemorySaveState) -> MemorySaveState:
        message = await memory_stream.add_message(state.content, state.user_id)
        return state.update(message_id=message.id)

    async def create_observation(self, state: MemorySaveState) -> MemorySaveState:
        # 원본 메시지 → 검색 친화적 Observation 변환
        obs_content = await llm.convert_to_observation(state.message_content)
        observation = await memory_stream.create_observation(obs_content, state.message_id)
        return state.update(observation_id=observation.id)
```

## Emotional Snapshot 저장

```python
# Observation 저장 시 그 시점의 감정 상태 스냅샷 함께 저장
@dataclass
class EmotionalSnapshot:
    user_emotion_snapshot: Dict[str, float]  # joy, sadness, anger, surprise, fear, disgust
    ai_emotion_snapshot: Dict[str, float]
    emotional_valence: float    # -1.0(부정) ~ 1.0(긍정)
    emotional_arousal: float    # 각성 수준
    emotional_alignment: float  # 0.0 ~ 1.0 (사용자-AI 감정 일치도)
```

## Memory Suppression 패턴

```python
# 삭제 대신 disclosure_weight 낮춰 자연스럽게 억제
async def suppress_memory(memory_id: str, reason: str) -> None:
    await db.update(memory_id, {
        "disclosure_weight": 0.05,  # 검색 점수 대폭 감소
        "suppression_reason": reason
    })

# 억제된 기억 재활성화 (사용자가 직접 해당 주제 언급 시)
async def reactivate_suppressed_memory(memory_id: str) -> None:
    await db.update(memory_id, {"disclosure_weight": 0.5})  # 일시적 재활성화
```

## 컨텍스트 윈도우 관리

```python
# 200,000 토큰 초과 시 Memory_Strength 낮은 기억부터 제거
async def prune_context(memories: List[Memory], max_tokens: int) -> List[Memory]:
    total_tokens = count_tokens(memories)
    if total_tokens <= max_tokens:
        return memories

    # Memory_Strength 오름차순 정렬 후 제거
    memories.sort(key=lambda m: m.memory_strength)
    while count_tokens(memories) > max_tokens:
        memories.pop(0)  # 가장 약한 기억 제거

    return memories
```

---

현재 작업: $ARGUMENTS
