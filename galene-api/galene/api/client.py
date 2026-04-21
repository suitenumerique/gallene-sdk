import httpx
from typing import Optional, Any
from urllib.parse import urljoin

from .exceptions import (
    GaleneBadRequestError,
    GaleneUnauthorizedError,
    GaleneForbiddenError,
    GaleneNotFoundError,
    GaleneConflictError,
    GaleneServerError,
    GaleneHttpError
)


class AsyncGaleneHttpClient:
    """
    Base asynchronous HTTP client for the Galene administration API.
    """
    def __init__(self, server_url: str, username: Optional[str] = None, password: Optional[str] = None):
        self.server_url = server_url.rstrip("/")
        
        auth = None
        if username and password:
            auth = (username, password)
            
        self._client = httpx.AsyncClient(
            base_url=self.server_url,
            auth=auth,
            headers={"Content-Type": "application/json"}
        )

    def _handle_response_error(self, response: httpx.Response):
        """Raises the appropriate GaleneError based on HTTP status code."""
        if response.status_code < 400:
            return

        status = response.status_code
        detail = response.text
        
        if status == 400:
            raise GaleneBadRequestError(f"Bad Request: {detail}", status)
        elif status == 401:
            raise GaleneUnauthorizedError(f"Unauthorized: {detail}", status)
        elif status == 403:
            raise GaleneForbiddenError(f"Forbidden: {detail}", status)
        elif status == 404:
            raise GaleneNotFoundError(f"Not Found: {detail}", status)
        elif status == 412:
            raise GaleneConflictError(f"Precondition Failed / Conflict: {detail}", status)
        elif status >= 500:
            raise GaleneServerError(f"Server Error: {detail}", status)
        else:
            raise GaleneHttpError(f"HTTP Error {status}: {detail}", status)

    async def get(self, path: str, **kwargs) -> httpx.Response:
        response = await self._client.get(path, **kwargs)
        self._handle_response_error(response)
        return response

    async def put(self, path: str, **kwargs) -> httpx.Response:
        response = await self._client.put(path, **kwargs)
        self._handle_response_error(response)
        return response

    async def post(self, path: str, **kwargs) -> httpx.Response:
        response = await self._client.post(path, **kwargs)
        self._handle_response_error(response)
        return response

    async def delete(self, path: str, **kwargs) -> httpx.Response:
        response = await self._client.delete(path, **kwargs)
        self._handle_response_error(response)
        return response

    async def head(self, path: str, **kwargs) -> httpx.Response:
        response = await self._client.head(path, **kwargs)
        self._handle_response_error(response)
        return response

    async def close(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
