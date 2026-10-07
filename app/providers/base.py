import asyncio
from abc import ABC, abstractmethod
from typing import TypeVar
from collections.abc import Awaitable, Callable

from pydantic import BaseModel
from app.config.schemas import Message
from app.exceptions.exception import (
    LLMError,
    LLMTimeoutError,
    # LLMConnectionError,
    # LLMRateLimitError,
    # LLMAuthenticationError,
    # LLMInvalidRequestError,
    # LLMModelNotFoundError,
    # LLMProviderUnavailableError,
    # LLMResponseError,
)

T = TypeVar("T", bound=BaseModel)
# This defines a type placeholder named T that must be BaseModel or one of its subclasses.
#   - TypeVar creates a type variable—a placeholder for a type.
#   - "T" names the type variable. It matches the variable on the left.
#   - bound=BaseModel restricts it to Pydantic models.

StructuredT = TypeVar("StructuredT", bound=BaseModel)


class LLMProvider(ABC):
    """
    Defines a shared contract for all LLM providers.
    Each provider—such as Ollama or OpenAI—must supply the same properties and method.

    ABC means Abstract Base Class.
    It describes what a provider must implement without providing the actual API-calling logic.

    Python prevents you from creating an instance until all its abstract members are
    implemented.
    """

    def __init__(self, timeout_seconds: float) -> None:
        self.timeout_seconds = timeout_seconds

    # @property means you access it like an attribute:
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        pass

    #  @abstractmethod marks something that each concrete provider must implement, if you don't add it, the method or property will be optional to override.
    # Generate a response from the model, given a list of messages.
    @abstractmethod
    async def generate(
        self,
        messages: list[Message],
        model: str | None = None,
    ) -> str:
        pass

    # //Generate structured output from the model, validated against a Pydantic schema.
    @abstractmethod
    async def generate_structured(
        self,
        messages: list[Message],
        output_schema: type[T],
        model: str | None = None,
    ) -> StructuredT:
        pass

    async def _with_timeout(
        self,
        operation: Callable[[], Awaitable[T]],
    ) -> T:
        try:
            # establishes a time limit for the code inside the block
            async with asyncio.timeout(self.timeout_seconds):
                return await operation()

        # handler converts it into an application-specific error
        except TimeoutError as exc:
            raise LLMTimeoutError(
                f"{self.name} request timed out.",
                provider=self.name,
            ) from exc

    @abstractmethod
    def _translate_error(
        self,
        exc: Exception,
    ) -> Exception:
        pass

    async def _execute(
        self,
        operation: Callable[[],Awaitable[T]],
    ) -> T:

        try:
            async with asyncio.timeout(
                self.timeout_seconds
            ):
                return await operation()

        except LLMError:
            raise  # re-raise the timeout error without modification, A bare raise re-raises the exception currently being handled.

        except TimeoutError as exc:
            raise LLMTimeoutError(
                f"{self.name} request timed out.",
                provider=self.name,
            ) from exc

        except Exception as exc:

            translated = (
                self._translate_error(exc)
            )

            # checks whether these are the exact same object.
            if translated is exc:
                raise

            # If the translator created a custom error, this raises that error while preserving the original exception as its cause for debugging.
            raise translated from exc


# Every provider must supply these three members:

#      Member           Purpose
#     ━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#      name             Returns the provider’s name as a string.
#     ───────────────  ──────────────────────────────────────────────────────────────────
#      default_model    Returns its default model name as a string.
#     ───────────────  ──────────────────────────────────────────────────────────────────
#      generate(...)    Sends a message to a model and returns its response as a string.

#     The generate signature adds a few details:

#     - async def means it’s asynchronous; callers use await provider.generate
#     - message: str expects a text message.
#     - model: str \| None = None accepts a model name or None, and may be omitted. The concrete provider decides how to handle None, typically by using its default model.
#     - -> str indicates that the awaited result should be a string.
#     - pass is a placeholder; the actual implementation belongs in each provider.

#     This lets the rest of your app call generate the same way regardless of which provider it uses. The provider handles the differences between APIs.


# _with_timeout - runs an asynchronous operation with a time limit. If it takes too long, it raises your custom LLMTimeoutError.


# -----
#   - The leading _ means this is intended as an internal helper.
#   - operation is a function you pass in.
#   - Callable[[], Awaitable[T]] means “a function that takes no arguments and returns something we can await, whose result has type T.”
#   - -> T means this helper returns that same result.
