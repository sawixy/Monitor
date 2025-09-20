import asyncio
from dotenv import load_dotenv
import sys
from config.config import ConfigFactory
from repository.repository import RepositoryFactory
from provider.provider import ProviderFactory
from bot import start

async def main():
    load_dotenv()

    if len(sys.argv) < 3:
        raise ValueError("Usage: python main.py <config_path> <repo_type> [connection_string]")
    
    config_factory = ConfigFactory()
    repository_factory = RepositoryFactory()
    provider_factory = ProviderFactory()

    repo_path = sys.argv[2]
    await repository_factory.create_repository(repo_path)
    await provider_factory.create_provider("")
    await config_factory.load_config(sys.argv[1])
    
    config = config_factory.get_config()
    repository = repository_factory.get_repository()
    provider = provider_factory.get_provider()

    if config == None: raise ValueError("Failed to get config")
    if repository == None: raise ValueError("Failed to get repository")
    if provider == None: raise ValueError("Failed to get provider")

    await start(config, repository, provider)

if __name__ == "__main__":
    asyncio.run(main())