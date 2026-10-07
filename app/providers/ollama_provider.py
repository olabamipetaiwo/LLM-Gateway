import ollama
from ollama import AsyncClient
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


class OllamaProvider(LLMProvider):

    def __init__(
        self,
        host: str,
        default_model: str,
        timeout_seconds: float,
    ):
        self.client = AsyncClient(host=host)
        self._default_model = default_model
        self.timeout_seconds = timeout_seconds

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def default_model(self) -> str:
        return self._default_model

    async def generate(
        self,
        messages: list[Message],
        model: str | None = None,
    ) -> str:
        selected_model = model or self.default_model

        ollama_messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]

        async def operation():
            return await self.client.chat(
                model=selected_model, messages=ollama_messages
            )

        response = await self._execute(operation)
        return response.message.content

        # try:
        #     response = await self._execute(operation)

        # except LLMTimeoutError:
        #     raise

        # except Exception as exc:
        #     translated = self._translate_error(exc)

        #     if translated is exc:
        #         raise

        #     raise translated from exc

        # response = await self._execute(operation)
        # return response.message.content

    async def generate_structured(
        self,
        messages: list[Message],
        output_schema: type[T],
        model: str | None = None,
    ) -> T:

        selected_model = model or self.default_model

        ollama_messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]

        response = await self.client.chat(
            model=selected_model,
            messages=ollama_messages,
            format=output_schema.model_json_schema(),
            options={
                "temperature": 0,
            },
        )

        return output_schema.model_validate_json(response.message.content)

    def _translate_error(
        self,
        exc: Exception,
    ) -> Exception:

        if isinstance(
            exc,
            ConnectionError,
        ):
            return LLMConnectionError(
                "Could not connect to local Ollama.",
                provider=self.name,
            )

        if isinstance(
            exc,
            ollama.ResponseError,
        ):
            status = exc.status_code

            if status == 404:
                return LLMModelNotFoundError(
                    "Requested Ollama model was not found.",
                    provider=self.name,
                )

            if status == 429:
                return LLMRateLimitError(
                    "Ollama rate limit exceeded.",
                    provider=self.name,
                )

            if status is not None and (400 <= status < 500):
                return LLMInvalidRequestError(
                    "Ollama rejected the request.",
                    provider=self.name,
                )

            if status is not None and (status >= 500):
                return LLMProviderUnavailableError(
                    "Ollama is temporarily unavailable.",
                    provider=self.name,
                )

            return LLMResponseError(
                "Ollama returned an unexpected error.",
                provider=self.name,
            )

        return exc
