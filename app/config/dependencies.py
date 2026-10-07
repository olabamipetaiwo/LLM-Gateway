from functools import lru_cache

from app.config.config import get_settings
from app.config.retry import RetryPolicy
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.registry import ProviderRegistry
from app.services.llm_service import LLMService


@lru_cache(maxsize=1)
def get_llm_service() -> LLMService:
    settings = get_settings()
    registry = ProviderRegistry()

    retry_policy = RetryPolicy(
        max_attempts=settings.llm_max_attempts,
        initial_delay=(settings.llm_retry_initial_delay),
        max_delay=(settings.llm_retry_max_delay),
    )

    registry.register(
        OllamaProvider(
            host=settings.ollama_host,
            default_model=settings.ollama_model,
            timeout_seconds=settings.llm_timeout_seconds,
        )
    )

    if settings.openai_api_key:
        registry.register(
            OpenAIProvider(
                settings.openai_api_key,
                settings.openai_model,
                timeout_seconds=settings.llm_timeout_seconds,
            )
        )
    if settings.anthropic_api_key:
        registry.register(
            AnthropicProvider(
                api_key=settings.anthropic_api_key,
                default_model=settings.anthropic_model,
                max_output_tokens=settings.max_output_tokens,
                timeout_seconds=settings.llm_timeout_seconds,
            )
        )
    if settings.gemini_api_key:
        registry.register(
            GeminiProvider(
                settings.gemini_api_key,
                settings.gemini_model,
                timeout_seconds=settings.llm_timeout_seconds,
            )
        )

    return LLMService(
        registry=registry, 
        default_provider=settings.default_provider, 
        retry_policy=retry_policy
    )


