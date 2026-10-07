

class LLMError(Exception):
    """Base exception for all LLM gateway failures."""

    #  * means parameters after it must be supplied by name
    # LLMError("Model not found", provider="ollama")  # Valid
    #  LLMError("Model not found", "ollama")           # TypeError
    # super().__init__(message) calls the parent Exception constructor. This sets up the standard exception message, so:

    #   str(error)  # "Model not found"

    def __init__(
        self,
        message: str,
        *,
        provider: str | None = None
    ):
        super().__init__(message)
        self.message = message
        self.provider = provider


class LLMTimeoutError(LLMError):
    pass


class LLMConnectionError(LLMError):
    pass


class LLMRateLimitError(LLMError):
    pass


class LLMAuthenticationError(LLMError):
    pass


class LLMInvalidRequestError(LLMError):
    pass


class LLMModelNotFoundError(LLMError):
    pass


class LLMProviderUnavailableError(LLMError):
    pass


class LLMResponseError(LLMError):
    pass
