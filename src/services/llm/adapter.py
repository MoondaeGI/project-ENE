"""LLMAdapter — provider registry with automatic fallback and retry."""

from __future__ import annotations

import asyncio
import logging
from typing import AsyncIterator

from core.exceptions import (
    LLMAllProvidersFailedError,
    LLMError,
    LLMProviderNotFoundError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from services.llm.providers.base import LLMProvider, LLMRequest, LLMResponse

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RATE_LIMIT_BACKOFF_BASE = 2.0  # seconds; doubles each retry


class LLMAdapter:
    """Central gateway for all LLM calls.

    Providers are registered by name. When a call fails, the adapter
    automatically falls back to other registered providers in registration
    order, retrying each up to MAX_RETRIES times.

    Example::

        adapter = LLMAdapter()
        adapter.register_provider("openai", OpenAIProvider(...))
        adapter.set_default_provider("openai")

        response = await adapter.generate(request)
    """

    def __init__(self) -> None:
        self._providers: dict[str, LLMProvider] = {}
        self._default_provider: str | None = None

    # ── Registry ──────────────────────────────────────────────────────────────

    def register_provider(self, name: str, provider: LLMProvider) -> None:
        """Register an LLM provider under *name*.

        Args:
            name: Unique identifier for the provider (e.g. "openai").
            provider: Object implementing the LLMProvider protocol.
        """
        self._providers[name] = provider
        logger.info("LLM provider registered: %s", name)

    def set_default_provider(self, name: str) -> None:
        """Set the default provider used when no explicit provider is requested.

        Args:
            name: Must match a previously registered provider name.

        Raises:
            LLMProviderNotFoundError: If *name* is not registered.
        """
        if name not in self._providers:
            raise LLMProviderNotFoundError(f"Provider '{name}' is not registered.")
        self._default_provider = name
        logger.info("Default LLM provider set to: %s", name)

    # ── Public API ────────────────────────────────────────────────────────────

    async def generate(
        self,
        request: LLMRequest,
        provider: str | None = None,
    ) -> LLMResponse:
        """Generate a completion, with automatic fallback across providers.

        Tries the requested provider first (or the default), then falls back
        to remaining registered providers in registration order.  Each
        provider is retried up to MAX_RETRIES times on transient errors.

        Args:
            request: Fully populated LLMRequest.
            provider: Override the default provider by name. Optional.

        Returns:
            LLMResponse from the first provider that succeeds.

        Raises:
            LLMProviderNotFoundError: If the named provider is not registered.
            LLMAllProvidersFailedError: If every provider fails.
        """
        ordered = self._get_provider_order(provider)
        last_error: Exception = LLMError("No providers registered.")

        for name in ordered:
            try:
                response = await self._generate_with_retry(name, request)
                return response
            except LLMError as exc:
                logger.warning("Provider '%s' failed: %s", name, exc)
                last_error = exc

        raise LLMAllProvidersFailedError(
            f"All providers failed. Last error: {last_error}"
        ) from last_error

    async def stream(
        self,
        request: LLMRequest,
        provider: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream completion tokens, falling back to the next provider on failure.

        Args:
            request: Fully populated LLMRequest.
            provider: Override the default provider by name. Optional.

        Yields:
            Incremental text chunks.

        Raises:
            LLMProviderNotFoundError: If the named provider is not registered.
            LLMAllProvidersFailedError: If every provider fails to start streaming.
        """
        ordered = self._get_provider_order(provider)
        last_error: Exception = LLMError("No providers registered.")

        for name in ordered:
            try:
                async for chunk in await self._stream_with_retry(name, request):
                    yield chunk
                return
            except LLMError as exc:
                logger.warning("Streaming provider '%s' failed: %s", name, exc)
                last_error = exc

        raise LLMAllProvidersFailedError(
            f"All providers failed during streaming. Last error: {last_error}"
        ) from last_error

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _get_provider_order(self, preferred: str | None) -> list[str]:
        """Return provider names ordered with *preferred* first.

        Args:
            preferred: Explicit provider name, or None to use the default.

        Returns:
            Ordered list of provider names to try.

        Raises:
            LLMProviderNotFoundError: If *preferred* is given but not registered.
        """
        if not self._providers:
            raise LLMAllProvidersFailedError("No providers are registered.")

        first = preferred or self._default_provider
        if first is None:
            first = next(iter(self._providers))

        if first not in self._providers:
            raise LLMProviderNotFoundError(f"Provider '{first}' is not registered.")

        rest = [n for n in self._providers if n != first]
        return [first, *rest]

    async def _generate_with_retry(
        self,
        name: str,
        request: LLMRequest,
    ) -> LLMResponse:
        """Call generate on *name* with exponential backoff on rate-limit errors.

        Args:
            name: Registered provider name.
            request: LLMRequest to send.

        Returns:
            LLMResponse on success.

        Raises:
            LLMError: After MAX_RETRIES failures.
        """
        provider = self._providers[name]
        last_error: Exception = LLMError("Unknown error")

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return await provider.generate(request)
            except LLMRateLimitError as exc:
                wait = RATE_LIMIT_BACKOFF_BASE ** attempt
                logger.warning(
                    "Rate limit on '%s' (attempt %d/%d), waiting %.1fs",
                    name, attempt, MAX_RETRIES, wait,
                )
                await asyncio.sleep(wait)
                last_error = exc
            except LLMTimeoutError as exc:
                logger.warning(
                    "Timeout on '%s' (attempt %d/%d)", name, attempt, MAX_RETRIES
                )
                last_error = exc
            except LLMError as exc:
                last_error = exc
                break  # Non-transient error — skip remaining retries

        raise last_error

    async def _stream_with_retry(
        self,
        name: str,
        request: LLMRequest,
    ) -> AsyncIterator[str]:
        """Return a streaming iterator from *name* with retry on rate-limit.

        Args:
            name: Registered provider name.
            request: LLMRequest to send.

        Returns:
            AsyncIterator[str] from the provider.

        Raises:
            LLMError: After MAX_RETRIES failures to initiate streaming.
        """
        provider = self._providers[name]
        last_error: Exception = LLMError("Unknown error")

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return provider.stream(request)
            except LLMRateLimitError as exc:
                wait = RATE_LIMIT_BACKOFF_BASE ** attempt
                logger.warning(
                    "Rate limit on '%s' (attempt %d/%d), waiting %.1fs",
                    name, attempt, MAX_RETRIES, wait,
                )
                await asyncio.sleep(wait)
                last_error = exc
            except LLMTimeoutError as exc:
                logger.warning(
                    "Timeout on '%s' (attempt %d/%d)", name, attempt, MAX_RETRIES
                )
                last_error = exc
            except LLMError as exc:
                last_error = exc
                break

        raise last_error
