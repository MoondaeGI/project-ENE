# Common Patterns

## Memory Evolution Pattern

주기적으로 실행되는 기억 진화 프로세스 (예: 매일 자정):

```python
async def apply_daily_memory_evolution(user_id: str):
    # 1. 오래된 기억 감쇠
    decayed_memories = await memory_evolution.decay_unused_memories(
        user_id,
        threshold_days=30
    )

    # 2. User Portrait 재생성
    recent_reflections = await memory_stream.get_recent_reflections(user_id, days=7)
    updated_portrait = await portrait_manager.update_portrait(
        user_id,
        recent_reflections
    )

    # 3. 낮은 강도의 기억 아카이브 (선택적)
    weak_memories = await memory_evolution.get_weak_memories(
        user_id,
        strength_threshold=0.1
    )
    await archive_memories(weak_memories)
```

## User Portrait Building Pattern

```python
async def build_user_portrait(user_id: str):
    reflections = await memory_stream.get_all_reflections(user_id)

    personality_reflections = filter_by_category(reflections, "personality")
    style_reflections = filter_by_category(reflections, "communication")
    interest_reflections = filter_by_category(reflections, "interests")

    portrait = await llm.synthesize_portrait({
        "personality": personality_reflections,
        "style": style_reflections,
        "interests": interest_reflections
    })

    portrait.confidence_score = calculate_confidence(reflections)
    return portrait
```

## Memory Strength Calculation Pattern

```python
def calculate_memory_strength(memory, current_time, decay_rate=0.01):
    hours_since_creation = (current_time - memory.created_at).total_seconds() / 3600
    time_decay = math.exp(-decay_rate * hours_since_creation)

    access_reinforcement = min(0.5, memory.access_count * 0.05)

    memory_strength = memory.importance_score * time_decay + access_reinforcement
    return min(1.0, max(0.0, memory_strength))
```

## Retrieval with Memory Evolution Pattern

```python
async def retrieve_with_evolution(user_id: str, query: str, top_k: int = 10):
    query_embedding = await embedding_service.embed(query)
    candidate_memories = await vector_search(user_id, query_embedding, top_k * 2)

    current_time = datetime.now()
    for memory in candidate_memories:
        memory.strength = calculate_memory_strength(memory, current_time)
        memory.retrieval_score = calculate_retrieval_score(
            memory, query_embedding, current_time
        )

    top_memories = sorted(
        candidate_memories,
        key=lambda m: m.retrieval_score,
        reverse=True
    )[:top_k]

    for memory in top_memories:
        await reinforce_memory(memory.id)
        await record_access(memory.id, query)

    return top_memories
```

## Portrait-Aware Response Generation Pattern

```python
async def generate_personalized_response(
    user_id: str,
    message: str,
    retrieved_memories: List[Memory],
    persona: CharacterPersona
) -> str:
    portrait = await portrait_manager.get_portrait(user_id)

    context = f"""
    사용자 프로필:
    - 성격: {', '.join(portrait.personality_traits)}
    - 의사소통 스타일: {portrait.communication_style}
    - 선호도: {portrait.preferences}

    관련 기억:
    {format_memories(retrieved_memories)}

    현재 메시지: {message}
    """

    full_prompt = f"""
    {persona.system_prompt}

    {context}

    위 정보를 바탕으로 사용자의 성향에 맞는 자연스러운 응답을 생성하세요.
    """

    return await llm_adapter.generate(full_prompt)
```

## Reflection Generation Pattern

```python
async def check_and_generate_reflection(user_id: str, recent_memories: List[Memory]):
    importance_sum = sum(m.importance_score for m in recent_memories)

    if importance_sum >= REFLECTION_THRESHOLD:
        reflection = await llm.generate_reflection(recent_memories)
        reflection.importance_score = calculate_importance(reflection)
        await memory_stream.store_reflection(reflection)

        # Portrait 업데이트 트리거
        await portrait_manager.update_portrait(user_id, [reflection])
```
