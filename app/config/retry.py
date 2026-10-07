import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

from app.exceptions.exception import (
    LLMConnectionError,
    LLMProviderUnavailableError,
    LLMRateLimitError,
    LLMTimeoutError,
)

T = TypeVar("T")


RETRYABLE_ERRORS = (
    LLMConnectionError,
    LLMProviderUnavailableError,
    LLMRateLimitError,
    LLMTimeoutError
)


class RetryPolicy:

    def __init__(
        self,
        *,
        max_attempts: int,
        initial_delay: float,
        max_delay: float,
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay

    async def execute(
        self,
        operation: Callable[[], Awaitable[T]],
    ) -> T:

        for attempt in range(1,self.max_attempts + 1):
            try:
                return await operation()

            except RETRYABLE_ERRORS:

                if attempt == self.max_attempts:
                    raise

                delay = self._delay_for(attempt)

                await asyncio.sleep(delay)

        raise RuntimeError("Retry loop exited unexpectedly.")

    def _delay_for(
        self,
        attempt: int,
    ) -> float:

        exponential_delay = self.initial_delay * (2 ** (attempt - 1))

        capped_delay = min(
            exponential_delay,
            self.max_delay,
        )

        jitter = random.uniform(
            0,
            capped_delay,
        )

        return jitter
