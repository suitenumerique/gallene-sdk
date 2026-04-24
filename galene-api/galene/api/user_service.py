from typing import List
import httpx

from .client import AsyncGaleneHttpClient
from .models import UserDefinition, StatefulToken


class UserServiceClient:
    """
    Client for managing Galene users and stateful tokens within a group.
    """
    def __init__(self, http_client: AsyncGaleneHttpClient):
        self._http = http_client

    async def list_users(self, groupname: str) -> List[str]:
        """Returns a list of users in a group."""
        resp = await self._http.get(f"/galene-api/v0/.groups/{groupname}/.users/")
        return resp.json()

    async def get_user(self, groupname: str, username: str) -> UserDefinition:
        """Retrieves a user definition."""
        resp = await self._http.get(f"/galene-api/v0/.groups/{groupname}/.users/{username}")
        user = resp.json()
        permissions = list(user.get("permissions", []))
        return UserDefinition.model_validate({"permissions" : permissions})

    async def update_user(self, groupname: str, username: str, definition: UserDefinition) -> None:
        """Updates a user definition (permissions, etc). Does not set password."""
        await self._http.put(
            f"/galene-api/v0/.groups/{groupname}/.users/{username}",
            json=definition.model_dump(exclude_unset=True)
        )

    async def delete_user(self, groupname: str, username: str) -> None:
        """Deletes a user."""
        await self._http.delete(f"/galene-api/v0/.groups/{groupname}/.users/{username}")

    async def set_user_password(self, groupname: str, username: str, password_plaintext: str) -> None:
        """Sets a plain-text password for a user. Galene hashes it."""
        await self._http.post(
            f"/galene-api/v0/.groups/{groupname}/.users/{username}/.password",
            content=password_plaintext,
            headers={"Content-Type": "text/plain"}
        )

    async def list_tokens(self, groupname: str, username: str) -> List[str]:
        """Lists stateful tokens for a user."""
        resp = await self._http.get(f"/galene-api/v0/.groups/{groupname}/.users/{username}/.tokens/")
        return resp.json()

    async def get_token(self, groupname: str, username: str, token_name: str) -> StatefulToken:
        """Retrieves a stateful token."""
        resp = await self._http.get(f"/galene-api/v0/.groups/{groupname}/.users/{username}/.tokens/{token_name}")
        return StatefulToken.model_validate(resp.json())
