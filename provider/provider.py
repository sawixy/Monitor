from abc import ABC, abstractmethod
import importlib

class ProviderFactory:
    REGISTRY = {
        "scrapfly": "providers.scrapfly_provider.ScrapflyProvider",
        "scraper": "providers.scraper_provider.ScraperProvider", 
        "hexowatch": "providers.hexowatch_provider.HexowatchProvider"
    }

    def __init__(self):
        self.provider: ProviderSystem = None

    async def create_provider(self, provider_type: str):
        if provider_type not in self.REGISTRY:
            raise ValueError(f"Unsupported provider type: {provider_type}")

        module_path, class_name = self.REGISTRY[provider_type].rsplit('.', 1)
        module = importlib.import_module(module_path)
        provider_class = getattr(module, class_name)

        self.provider = provider_class()

    def get_provider(self) -> 'ProviderSystem':
        if self.provider is None:
            raise ValueError("Provider not created. Call create_provider() first.")
        return self.provider

class ProviderSystem(ABC):
    @abstractmethod
    async def init(self, **kwargs) -> None:
        """Initialize provider with configuration"""
        pass

    @abstractmethod
    async def check(self, url: str) -> dict:
        """
        Check provided URL and return results
        
        Returns:
            dict: {
                'status': int, 
                'error': Optional[str],
                'response_time': int,
                'ssl_valid': bool
            }
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close provider connection and release resources"""
        pass

    async def __aenter__(self):
        """Async context manager support"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Automatically close on exit"""
        await self.close()