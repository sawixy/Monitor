from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import importlib

class RepositoryFactory:
    REGISTRY = {
        "db": "repository.sqlite_repository.SqliteRepository",
        "json": "repository.json_repository.Json"
    }

    def __init__(self):
        self.repository: RepositorySystem = None

    async def create_repository(self, repo_path: str = None):
        repo_ext = repo_path.split(".")[-1].lower()

        if repo_ext not in self.REGISTRY:
            raise ValueError(f"Unsupported repository type: {repo_ext}")

        module_path, class_name = self.REGISTRY[repo_ext].rsplit('.', 1)
        module = importlib.import_module(module_path)
        repository_class = getattr(module, class_name)

        self.repository = repository_class()
        await self.repository.init(repo_path)

    def get_repository(self) -> 'RepositorySystem':
        if self.repository is None:
            raise ValueError("Repository not created. Call create_repository() first.")
        return self.repository


class RepositorySystem(ABC):
    @abstractmethod
    async def init(self, path):
        """Initializing repository"""
        pass

    @abstractmethod
    async def add_site(self, url: str, alias: str) -> None:
        """Add a new site to monitor"""
        pass

    @abstractmethod
    async def add_check(self, alias: str, status: int, 
                      error: Optional[str], time: int, ssl_warn: bool) -> None:
        """Add a new check result"""
        pass

    @abstractmethod
    async def delete_site(self, url: str) -> None:
        """Delete a site"""
        pass

    @abstractmethod
    async def delete_checks(self) -> None:
        """Delete a check result"""
        pass

    @abstractmethod
    async def get_url(self, alias: str) -> Optional[Tuple[str, str]]:
        """Get a site by alias"""
        pass

    @abstractmethod
    async def get_check(self, check_id: int) -> Optional[Tuple]:
        """Get a check by ID"""
        pass

    @abstractmethod
    async def set_site(self, alias: str, new_url: str) -> None:
        """Update a site's URL"""
        pass

    @abstractmethod
    async def get_all_sites(self) -> List[Tuple[str, str]]:
        """Get all sites"""
        pass

    @abstractmethod
    async def get_all_checks(self, alias: str) -> List[Tuple]:
        """Get all checks for a site"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close repository"""
        pass