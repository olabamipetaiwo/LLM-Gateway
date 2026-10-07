import pytest

from app.config.retry import RetryPolicy
from tests.fakes import FlakyProvider


@pytest.mark.asyncio
async def test_retries_transient_failure():

    provider = FlakyProvider(
        failures_before_success=2
    )

    policy = RetryPolicy(
        max_attempts=3,
        initial_delay=0,
        max_delay=0,
    )

    result = await policy.execute(
        lambda: provider.generate([])
    )

    assert result == "success"
    assert provider.calls == 3