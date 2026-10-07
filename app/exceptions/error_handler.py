from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.exception import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMError,
    LLMInvalidRequestError,
    LLMModelNotFoundError,
    LLMProviderUnavailableError,
    LLMRateLimitError,
    LLMResponseError,
    LLMTimeoutError,
)


# THis file turns your application exceptions into HTTP responses** that the API client can understand.
def llm_error_response(
    status_code: int,
    code: str,
    exc: LLMError,
) -> JSONResponse:

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": exc.message,
                "provider": exc.provider,
            }
        },
    )


def register_error_handlers(app):

    @app.exception_handler(LLMTimeoutError)
    async def timeout_handler(
        request: Request,
        exc: LLMTimeoutError,
    ):
        return llm_error_response(
            504,
            "llm_timeout",
            exc,
        )

    @app.exception_handler(LLMConnectionError)
    async def connection_handler(
        request: Request,
        exc: LLMConnectionError,
    ):
        return llm_error_response(
            503,
            "llm_connection_error",
            exc,
        )

    @app.exception_handler(LLMRateLimitError)
    async def rate_limit_handler(
        request: Request,
        exc: LLMRateLimitError,
    ):
        return llm_error_response(
            429,
            "llm_rate_limit",
            exc,
        )

    @app.exception_handler(LLMAuthenticationError)
    async def auth_handler(
        request: Request,
        exc: LLMAuthenticationError,
    ):
        return llm_error_response(
            502,
            "llm_provider_authentication",
            exc,
        )

    @app.exception_handler(LLMInvalidRequestError)
    async def invalid_request_handler(
        request: Request,
        exc: LLMInvalidRequestError,
    ):
        return llm_error_response(
            400,
            "llm_invalid_request",
            exc,
        )

    @app.exception_handler(LLMModelNotFoundError)
    async def model_handler(
        request: Request,
        exc: LLMModelNotFoundError,
    ):
        return llm_error_response(
            400,
            "llm_model_not_found",
            exc,
        )

    @app.exception_handler(LLMProviderUnavailableError)
    async def unavailable_handler(
        request: Request,
        exc: LLMProviderUnavailableError,
    ):
        return llm_error_response(
            503,
            "llm_provider_unavailable",
            exc,
        )

    @app.exception_handler(LLMResponseError)
    async def response_handler(
        request: Request,
        exc: LLMResponseError,
    ):
        return llm_error_response(
            502,
            "llm_provider_error",
            exc,
        )
