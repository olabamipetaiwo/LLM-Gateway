from app.providers.registry import ProviderRegistry
from app.config.retry import RetryPolicy
from app.config.schemas import Message
from app.providers.base import T


class LLMService:
    def __init__(
        self,
        registry: ProviderRegistry,
        default_provider: str,
        retry_policy: RetryPolicy,
    ):
        self.registry = registry
        self.default_provider = default_provider
        self.retry_policy = retry_policy

    async def chat(
        self,
        messages: list[Message],
        provider_name: str | None = None,
        model: str | None = None,
    ) -> tuple[str, str, str]:

        selected_provider_name = provider_name or self.default_provider

        provider = self.registry.get(selected_provider_name)

        selected_model = model or provider.default_model

        async def operation():
            return await provider.generate(
                messages=messages,
                model=selected_model,
            )

        content = await self.retry_policy.execute(operation)

        return (
            content,
            provider.name,
            selected_model,
        )

    async def structured(
        self,
        messages: list[Message],
        output_schema: type[T],
        provider_name: str | None = None,
        model: str | None = None,
    ) -> tuple[T, str, str]:

        selected_provider_name = provider_name or self.default_provider

        provider = self.registry.get(selected_provider_name)

        selected_model = model or provider.default_model

        async def operation():
            return (
                await provider.generate_structured(
                    messages=messages,
                    output_schema=output_schema,
                    model=selected_model,
                )
            )

        result = await self.retry_policy.execute(operation)

        return (
            result,
            provider.name,
            selected_model,
        )
