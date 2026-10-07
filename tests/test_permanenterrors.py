import pytest

from app.config.retry import RetryPolicy
from app.exceptions.exception import (
    LLMAuthenticationError,
)


@pytest.mark.asyncio
async def test_authentication_not_retried():

    calls = 0

    async def operation():
        nonlocal calls

        calls += 1

        raise LLMAuthenticationError("Invalid API key")

    policy = RetryPolicy(
        max_attempts=5,
        initial_delay=0,
        max_delay=0,
    )

    with pytest.raises(LLMAuthenticationError):
        await policy.execute(operation)

    assert calls == 1
