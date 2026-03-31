"""LLMProvider protocol and shared data structures for the LLM abstraction layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import AsyncIterator, Literal, Protocol, runtime_checkable

LLMRole = Literal["system", "user", "assistant"]


@dataclass
class LLMMessage:
    """A single message in a conversation turn.

    Attributes:
        role: Speaker role — "system", "user", or "assistant".
        content: Text content of the message.
    """

    role: LLMRole
    content: str


@dataclass
class LLMRequest:
    """Input to an LLM provider call.

    Attributes:
        messages: Ordered list of conversation messages.
        model: Model identifier (e.g. "gpt-4o").
        temperature: Sampling temperature in [0, 2].
        max_tokens: Maximum tokens to generate; None means provider default.
    """

    messages: list[LLMMessage]
    model: str
    temperature: float = 0.7
    max_tokens: int | None = None


@dataclass
class LLMResponse:
    """Output from an LLM provider call.

    Attributes:
        content: Generated text.
        model: Model that produced the response.
        prompt_tokens: Tokens consumed by the prompt.
        completion_tokens: Tokens produced in the completion.
    """

    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int

    @property
    def total_tokens(self) -> int:
        """Total tokens used (prompt + completion)."""
        return self.prompt_tokens + self.completion_tokens


@runtime_checkable
class LLMProvider(Protocol):
    """Strategy interface for LLM providers.

    Each concrete provider (OpenAI, Anthropic, …) must implement all three
    methods.  The protocol is marked ``runtime_checkable`` so that
    ``isinstance`` checks work in the adapter's registry.
    """

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a completion for the given request.

        Args:
            request: Fully populated LLMRequest.

        Returns:
            LLMResponse with the generated content and token counts.

        Raises:
            LLMRateLimitError: Provider returned a rate-limit error.
            LLMContextWindowExceededError: Request exceeds context window.
            LLMTimeoutError: Provider call timed out.
            LLMError: Any other provider-level failure.
        """
        ...

    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Stream completion tokens for the given request.

        Args:
            request: Fully populated LLMRequest.

        Yields:
            Incremental text chunks as they arrive from the provider.

        Raises:
            LLMRateLimitError: Provider returned a rate-limit error.
            LLMContextWindowExceededError: Request exceeds context window.
            LLMTimeoutError: Provider call timed out.
            LLMError: Any other provider-level failure.
        """
        ...

    def get_token_count(self, text: str) -> int:
        """Return the token count for *text* using this provider's tokeniser.

        Args:
            text: Raw text string to count tokens for.

        Returns:
            Integer token count.
        """
        ...
