import anthropic
from anthropic import AsyncAnthropic
from app.config.schemas import Message
from app.providers.base import LLMProvider
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


class AnthropicProvider(LLMProvider):

    def __init__(
        self,
        api_key: str,
        default_model: str,
        max_output_tokens: int,
        timeout_seconds: float,
    ) -> None:
        self.client = AsyncAnthropic(
            api_key=api_key,
        )
        self._default_model = default_model
        self._max_output_tokens = max_output_tokens
        self.timeout_seconds = timeout_seconds

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def default_model(self) -> str:
        return self._default_model

    async def generate(
        self,
        messages: list[Message],
        model: str | None = None,
    ) -> str:
        selected_model = model or self.default_model

        system_parts: list[str] = []
        conversation_messages = []

        for message in messages:

            if message.role == "system":
                system_parts.append(message.content)

            else:
                conversation_messages.append(
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                )

        system_prompt = "\n\n".join(system_parts)

        async def operation():
            return await self.client.responses.create(
                model=selected_model,
                max_tokens=self._max_output_tokens,
                system=system_prompt or None,
                messages=conversation_messages,
            )

        response = await self._execute(operation)

        text_blocks = [block.text for block in response.content if block.type == "text"]
        return "".join(text_blocks)

    async def generate_structured(
        self,
        messages: list[Message],
        output_schema: type[T],
        model: str | None = None,
    ) -> T:

        selected_model = model or self.default_model

        system_parts = []
        conversation_messages = []

        for message in messages:

            if message.role == "system":
                system_parts.append(message.content)

            else:
                conversation_messages.append(
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                )

        response = await self.client.messages.create(
            model=selected_model,
            max_tokens=self._max_output_tokens,
            system="\n\n".join(system_parts) or None,
            messages=conversation_messages,
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": output_schema.model_json_schema(),
                }
            },
        )

        text = "".join(block.text for block in response.content if block.type == "text")

        return output_schema.model_validate_json(text)

    def _translate_error(
        self,
        exc: Exception,
    ) -> Exception:

        if isinstance(
            exc,
            anthropic.APITimeoutError,
        ):
            return LLMTimeoutError(
                "Anthropic request timed out.",
                provider=self.name,
            )

        if isinstance(
            exc,
            anthropic.RateLimitError,
        ):
            return LLMRateLimitError(
                "Anthropic rate limit exceeded.",
                provider=self.name,
            )

        if isinstance(
            exc,
            anthropic.AuthenticationError,
        ):
            return LLMAuthenticationError(
                "Anthropic authentication failed.",
                provider=self.name,
            )

        if isinstance(
            exc,
            anthropic.NotFoundError,
        ):
            return LLMModelNotFoundError(
                "Requested Anthropic model was not found.",
                provider=self.name,
            )

        if isinstance(
            exc,
            anthropic.BadRequestError,
        ):
            return LLMInvalidRequestError(
                "Anthropic rejected the request.",
                provider=self.name,
            )

        if isinstance(
            exc,
            anthropic.APIConnectionError,
        ):
            return LLMConnectionError(
                "Could not connect to Anthropic.",
                provider=self.name,
            )

        if isinstance(
            exc,
            anthropic.APIStatusError,
        ):
            if exc.status_code >= 500:
                return LLMProviderUnavailableError(
                    "Anthropic is temporarily unavailable.",
                    provider=self.name,
                )

            return LLMResponseError(
                "Anthropic returned an unexpected API error.",
                provider=self.name,
            )

        return exc
