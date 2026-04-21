from typing import Optional
from .client import AsyncGaleneHttpClient
from .group_service import GroupServiceClient
from .user_service import UserServiceClient

class GaleneAPI:
    """
    Main entry point for the Galene administration API.
    Provides access to group and user services.
    """
    def __init__(self, server_url: str, username: Optional[str] = None, password: Optional[str] = None):
        self.http = AsyncGaleneHttpClient(server_url, username, password)
        self.groups = GroupServiceClient(self.http)
        self.users = UserServiceClient(self.http)

    async def close(self):
        await self.http.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
