from typing import List, Tuple, Optional
import httpx

from .client import AsyncGaleneHttpClient
from .models import GroupDefinition


class GroupServiceClient:
    """
    Client for managing Galene groups.
    """
    def __init__(self, http_client: AsyncGaleneHttpClient):
        self._http = http_client

    async def list_groups(self) -> List[str]:
        """Returns a list of all group names."""
        resp = await self._http.get("/galene-api/v0/.groups/")
        return resp.json()

    async def get_group(self, groupname: str) -> Tuple[GroupDefinition, str]:
        """
        Retrieves a group definition and its ETag.
        
        Returns:
            A tuple of (GroupDefinition, ETag_string)
        """
        resp = await self._http.get(f"/galene-api/v0/.groups/{groupname}")
        etag = resp.headers.get("ETag", "")
        return GroupDefinition.model_validate(resp.json()), etag


    async def create_group(self, groupname: str, definition: GroupDefinition) -> None:
        """Creates a new group.
        
        Args:
            groupname: The name of the group.
            definition: The group configuration.
        """
        await self._http.put(
            f"/galene-api/v0/.groups/{groupname}",
            json=definition.model_dump(exclude_unset=True),
            headers={"If-None-Match": "*"}
        )
        

    async def update_group(self, groupname: str, definition: GroupDefinition, etag: Optional[str] = None) -> None:
        """
        Updates or creates a group definition.
        
        Args:
            groupname: The name of the group.
            definition: The new group configuration.
            etag: If provided, will be sent as 'If-Match' to avoid overwriting recent changes. 
                  If creating a new group, you could use etag='*' as If-None-Match per Galene API conventions.
        """
        headers = {}
        if etag:
            if etag == "*":
                headers["If-None-Match"] = "*"
            else:
                headers["If-Match"] = etag
                
        await self._http.put(
            f"/galene-api/v0/.groups/{groupname}",
            json=definition.model_dump(exclude_unset=True),
            headers=headers
        )

    async def delete_group(self, groupname: str) -> None:
        """Deletes a group."""
        await self._http.delete(f"/galene-api/v0/.groups/{groupname}")

    async def set_auth_keys(self, groupname: str, jwk_set: dict) -> None:
        """
        Sets the JSON Web Key Set (JWKS) used for validation of stateless tokens (JWTs).
        
        Args:
            groupname: The name of the group.
            jwk_set: A dictionary representing the JWKS (RFC 7517).
        """
        await self._http.put(
            f"/galene-api/v0/.groups/{groupname}/.keys",
            json=jwk_set,
            headers={"Content-Type": "application/jwk-set+json"}
        )

    async def delete_auth_keys(self, groupname: str) -> None:
        """Deletes the authentication keys for a group."""
        await self._http.delete(f"/galene-api/v0/.groups/{groupname}/.keys")
