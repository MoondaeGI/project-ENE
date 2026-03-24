# LLM Adapter (LLM Abstraction Layer)

## 개요

Strategy 패턴을 사용하여 다양한 LLM 제공자를 추상화합니다. 런타임에 LLM 제공자를 동적으로 전환할 수 있습니다.

**현재 구현된 제공자**: OpenAI (기본)

**추후 추가 예정**: Anthropic, Google Gemini, Ollama, LM Studio, LocalAI

## LLMProvider 프로토콜

```python
class LLMProvider(Protocol):
    async def generate(self, prompt: str, **kwargs) -> str
    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]
    def get_token_count(self, text: str) -> int
```

## LLMAdapter 인터페이스

```python
class LLMAdapter:
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}

    def register_provider(self, name: str, provider: LLMProvider) -> None
    def set_default_provider(self, name: str) -> None

    async def generate(
        self,
        prompt: str,
        provider: Optional[str] = None,
        **kwargs
    ) -> str

    async def stream(
        self,
        prompt: str,
        provider: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]
```

## 사용 예시

```python
adapter = LLMAdapter()
adapter.register_provider("openai", OpenAIProvider(api_key=...))
adapter.set_default_provider("openai")

# 기본 제공자 사용
response = await adapter.generate("Hello")

# 추후: 다른 provider 등록 시 기존 코드 변경 없이 사용 가능
# adapter.register_provider("anthropic", AnthropicProvider(api_key=...))
# response = await adapter.generate("Hello", provider="anthropic")
```

## 에러 처리

- LLM 호출 실패 시 다른 Provider로 자동 전환
- 타임아웃 시 재시도 (최대 3회)
- Rate limit 초과 시 대기 후 재시도
- 컨텍스트 윈도우 초과 시 오래된 메시지부터 제거 (최소 최근 5개 메시지 유지)
