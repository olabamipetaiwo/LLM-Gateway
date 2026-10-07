from app.providers.base import LLMProvider


class ProviderRegistry:
    """
        Maintains a registry of LLM providers.
        It allows you to register providers and retrieve them by name.  
        
        Keeps your app decoupled from specific provider implementations, enabling easy switching or addition of providers.
    """
    def __init__(self):
        self._providers: dict[str, LLMProvider] = {}

    def register(self, provider: LLMProvider) -> None:
        self._providers[provider.name] = provider

    def get(self, name: str) -> LLMProvider:
        provider = self._providers.get(name)

        if provider is None:
            raise ValueError(f"Unknown provider: {name}")

        return provider
    
    def names(self) -> list[str]:
        return list(self._providers.keys())

