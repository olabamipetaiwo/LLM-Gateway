import openai
from openai import AsyncOpenAI
from app.providers.base import LLMProvider
from app.config.schemas import Message
from app.providers.base import T
from app.exceptions.exception import (
    LLMTimeoutError,
    LLMResponseError,
    LLMRateLimitError,
    LLMAuthenticationError,
    LLMInvalidRequestError,
    LLMModelNotFoundError,
    LLMProviderUnavailableError,
    LLMConnectionError,
)


class OpenAIProvider(LLMProvider):

    def __init__(
        self,
        api_key: str,
        default_model: str,
        timeout_seconds: float,
    ):
        self.client = AsyncOpenAI(api_key=api_key)
        self._default_model = default_model
        self.timeout_seconds = timeout_seconds

    @property
    def name(self) -> str:
        return "openai"

    @property
    def default_model(self) -> str:
        return self._default_model

    async def generate(
        self,
        messages: list[Message],
        model: str | None = None,
    ) -> str:
        selected_model = model or self.default_model

        input_messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]

        async def operation():
            return await self.client.responses.create(
                model=selected_model,
                input=input_messages,
            )

        response = await self._execute(operation)
        return response.output_text

    async def generate_structured(
        self,
        messages: list[Message],
        output_schema: type[T],
        model: str | None = None,
    ) -> T:

        selected_model = model or self.default_model

        input_messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]

        response = await self.client.responses.create(
            model=selected_model,
            input=input_messages,
            text={
                "format": {
                    "type": "json_schema",
                    "name": output_schema.__name__,
                    "schema": output_schema.model_json_schema(),
                    "strict": True,
                }
            },
        )

        return output_schema.model_validate_json(response.output_text)

    def _translate_error(
        self,
        exc: Exception,
    ) -> LLMResponseError | Exception:

        if isinstance(exc, openai.APITimeoutError):
            return LLMTimeoutError(
                "OpenAI request timed out.",
                provider=self.name,
            )

        if isinstance(exc, openai.RateLimitError):
            return LLMRateLimitError(
                "OpenAI rate limit exceeded.",
                provider=self.name,
            )

        if isinstance(exc, openai.AuthenticationError):
            return LLMAuthenticationError(
                "OpenAI authentication failed.",
                provider=self.name,
            )

        if isinstance(exc, openai.NotFoundError):
            return LLMModelNotFoundError(
                "Requested OpenAI resource or model was not found.",
                provider=self.name,
            )

        if isinstance(exc, openai.BadRequestError):
            return LLMInvalidRequestError(
                "OpenAI rejected the request.",
                provider=self.name,
            )

        if isinstance(exc, openai.APIConnectionError):
            return LLMConnectionError(
                "Could not connect to OpenAI.",
                provider=self.name,
            )

        if isinstance(exc, openai.APIStatusError):
            if exc.status_code >= 500:
                return LLMProviderUnavailableError(
                    "OpenAI is temporarily unavailable.",
                    provider=self.name,
                )

            return LLMResponseError(
                "OpenAI returned an unexpected API error.",
                provider=self.name,
            )

        return exc
