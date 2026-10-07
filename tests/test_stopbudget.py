import pytest

from app.config.retry import RetryPolicy
from app.exceptions.exception import LLMProviderUnavailableError
from tests.fakes import FlakyProvider


@pytest.mark.asyncio
async def test_retry_budget_exhausted():

    provider = FlakyProvider(failures_before_success=10)

    policy = RetryPolicy(
        max_attempts=3,
        initial_delay=0,
        max_delay=0,
    )

    with pytest.raises(LLMProviderUnavailableError):
        await policy.execute(lambda: provider.generate([]))

    assert provider.calls == 3
