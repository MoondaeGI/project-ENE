"""OpenAI implementation of the LLMProvider protocol."""

from __future__ import annotations

import logging
from typing import AsyncIterator

import tiktoken
from openai import AsyncOpenAI, APIStatusError, APITimeoutError

from core.exceptions import (
    LLMContextWindowExceededError,
    LLMError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from services.llm.providers.base import LLMProvider, LLMRequest, LLMResponse

logger = logging.getLogger(__name__)

# OpenAI HTTP status codes
_RATE_LIMIT_STATUS = 429
_CONTEXT_EXCEEDED_STATUS = 400
_CONTEXT_EXCEEDED_CODE = "context_length_exceeded"


class OpenAIProvider:
    """LLMProvider implementation backed by the OpenAI chat completions API.

    Attributes:
        _client: Async OpenAI client.
        _model: Default model identifier (e.g. "gpt-4o").
        _encoding: tiktoken encoding used for local token counting.
    """

    def __init__(self, api_key: str, model: str, embedding_model: str) -> None:
        """Initialise the provider with credentials and model configuration.

        Args:
            api_key: OpenAI API key (loaded from settings, never hardcoded).
            model: Chat completions model to use (e.g. "gpt-4o").
            embedding_model: Embedding model name (reserved for EmbeddingService).
        """
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._embedding_model = embedding_model
        # Use cl100k_base as a safe fallback for models without a specific encoding
        try:
            self._encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            self._encoding = tiktoken.get_encoding("cl100k_base")

    # ── LLMProvider protocol ──────────────────────────────────────────────────

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a chat completion via the OpenAI API.

        Args:
            request: Fully populated LLMRequest.

        Returns:
            LLMResponse containing the generated text and token usage.

        Raises:
            LLMRateLimitError: HTTP 429 from OpenAI.
            LLMContextWindowExceededError: context_length_exceeded error.
            LLMTimeoutError: Request timed out.
            LLMError: Any other API failure.
        """
        messages = _to_openai_messages(request)
        kwargs = _build_kwargs(request)

        try:
            completion = await self._client.chat.completions.create(
                model=request.model or self._model,
                messages=messages,
                stream=False,
                **kwargs,
            )
        except APITimeoutError as exc:
            raise LLMTimeoutError("OpenAI request timed out.") from exc
        except APIStatusError as exc:
            raise _map_api_error(exc) from exc

        choice = completion.choices[0]
        usage = completion.usage

        return LLMResponse(
            content=choice.message.content or "",
            model=completion.model,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
        )

    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Stream chat completion tokens from the OpenAI API.

        Args:
            request: Fully populated LLMRequest.

        Yields:
            Incremental text chunks as they arrive.

        Raises:
            LLMRateLimitError: HTTP 429 from OpenAI.
            LLMContextWindowExceededError: context_length_exceeded error.
            LLMTimeoutError: Request timed out.
            LLMError: Any other API failure.
        """
        messages = _to_openai_messages(request)
        kwargs = _build_kwargs(request)

        try:
            async with self._client.chat.completions.stream(
                model=request.model or self._model,
                messages=messages,
                **kwargs,
            ) as stream:
                async for chunk in stream:
                    delta = chunk.choices[0].delta.content if chunk.choices else None
                    if delta:
                        yield delta
        except APITimeoutError as exc:
            raise LLMTimeoutError("OpenAI streaming request timed out.") from exc
        except APIStatusError as exc:
            raise _map_api_error(exc) from exc

    def get_token_count(self, text: str) -> int:
        """Count tokens locally using tiktoken (no API call required).

        Args:
            text: Raw text to tokenise.

        Returns:
            Number of tokens according to this model's encoding.
        """
        return len(self._encoding.encode(text))


# ── Module-level helpers ──────────────────────────────────────────────────────


def _to_openai_messages(request: LLMRequest) -> list[dict[str, str]]:
    """Convert LLMRequest messages to the format expected by the OpenAI API.

    Args:
        request: Source LLMRequest.

    Returns:
        List of {"role": ..., "content": ...} dicts.
    """
    return [{"role": msg.role, "content": msg.content} for msg in request.messages]


def _build_kwargs(request: LLMRequest) -> dict:
    """Build optional keyword arguments for the OpenAI API call.

    Args:
        request: Source LLMRequest.

    Returns:
        Dict of optional parameters (temperature, max_tokens).
    """
    kwargs: dict = {"temperature": request.temperature}
    if request.max_tokens is not None:
        kwargs["max_tokens"] = request.max_tokens
    return kwargs


def _map_api_error(exc: APIStatusError) -> LLMError:
    """Map an OpenAI APIStatusError to a domain-specific LLMError.

    Args:
        exc: The raw APIStatusError raised by the openai library.

    Returns:
        The appropriate LLMError subclass instance.
    """
    if exc.status_code == _RATE_LIMIT_STATUS:
        return LLMRateLimitError(f"OpenAI rate limit exceeded: {exc.message}")

    if exc.status_code == _CONTEXT_EXCEEDED_STATUS:
        body = exc.body or {}
        code = body.get("error", {}).get("code", "") if isinstance(body, dict) else ""
        if code == _CONTEXT_EXCEEDED_CODE:
            return LLMContextWindowExceededError(
                f"OpenAI context window exceeded: {exc.message}"
            )

    return LLMError(f"OpenAI API error {exc.status_code}: {exc.message}")
