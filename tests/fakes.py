from pydantic import BaseModel

from app.exceptions.exception import (
    LLMProviderUnavailableError,
)
from app.providers.base import LLMProvider
from app.config.schemas import Message


class FlakyProvider(LLMProvider):

    def __init__(
        self,
        failures_before_success: int,
    ):
        super().__init__(timeout_seconds=5)

        self.failures_before_success = failures_before_success

        self.calls = 0

    @property
    def name(self) -> str:
        return "flaky"

    @property
    def default_model(self) -> str:
        return "fake-model"

    def _translate_error(
        self,
        exc: Exception,
    ) -> Exception:
        return exc

    async def generate(
        self,
        messages: list[Message],
        model: str | None = None,
    ) -> str:

        self.calls += 1

        if self.calls <= self.failures_before_success:
            raise (
                LLMProviderUnavailableError(
                    "Temporary failure",
                    provider=self.name,
                )
            )

        return "success"

    async def generate_structured(
        self,
        messages,
        output_schema: type[BaseModel],
        model=None,
    ):
        raise NotImplementedError
