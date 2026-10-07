from google import genai
from google.genai import errors
from google.genai import types
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


class GeminiProvider(LLMProvider):

    def __init__(
        self,
        api_key: str,
        default_model: str,
        timeout_seconds: float,
    ):
        self.client = genai.Client(
            api_key=api_key,
        )
        self._default_model = default_model
        self.timeout_seconds = timeout_seconds

    @property
    def name(self) -> str:
        return "gemini"

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
        contents: list[types.Content] = []

        for message in messages:

            if message.role == "system":
                system_parts.append(message.content)
                continue

            role = "model" if message.role == "assistant" else "user"

            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=message.content)],
                )
            )

        system_instruction = "\n\n".join(system_parts)

        config = types.GenerateContentConfig(
            system_instruction=(system_instruction or None)
        )

        async def operation():
            await self.client.aio.models.generate_content(
                model=selected_model,
                contents=contents,
                config=config,
            )

        response = await self._execute(operation)
        return response.text or ""

    async def generate_structured(
        self,
        messages: list[Message],
        output_schema: type[T],
        model: str | None = None,
    ) -> T:

        selected_model = model or self.default_model

        system_parts: list[str] = []
        contents: list[types.Content] = []

        for message in messages:

            if message.role == "system":
                system_parts.append(message.content)
                continue

            role = "model" if message.role == "assistant" else "user"

            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=message.content)],
                )
            )

        config = types.GenerateContentConfig(
            system_instruction=("\n\n".join(system_parts) or None),
            response_mime_type="application/json",
            response_schema=output_schema,
        )

        response = await self.client.aio.models.generate_content(
            model=selected_model,
            contents=contents,
            config=config,
        )

        return output_schema.model_validate_json(response.text)

    def _translate_error(
        self,
        exc: Exception,
    ) -> Exception:

        if isinstance(
            exc,
            errors.APIError,
        ):
            code = exc.code

            if code == 401:
                return LLMAuthenticationError(
                    "Gemini authentication failed.",
                    provider=self.name,
                )

            if code == 404:
                return LLMModelNotFoundError(
                    "Requested Gemini model was not found.",
                    provider=self.name,
                )

            if code == 429:
                return LLMRateLimitError(
                    "Gemini rate limit exceeded.",
                    provider=self.name,
                )

            if 400 <= code < 500:
                return LLMInvalidRequestError(
                    "Gemini rejected the request.",
                    provider=self.name,
                )

            if code >= 500:
                return LLMProviderUnavailableError(
                    "Gemini is temporarily unavailable.",
                    provider=self.name,
                )

            return LLMResponseError(
                "Gemini returned an unexpected API error.",
                provider=self.name,
            )

        return exc


# google.genai.errors.ClientError: 400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': "Role 'system' is not supported. Please use a valid role: MODEL, USER.", 'status': 'INVALID_ARGUMENT'}}
