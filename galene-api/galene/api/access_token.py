import time
from typing import List, Optional, Dict, Any

import jwt


class VideoGrants:
    """
    Represents the permissions/grants given to a Galene user.
    Unlike LiveKit which uses specific boolean flags, Galene uses a list
    of permission strings (e.g., ["present", "op", "record"]).
    """
    def __init__(self, room: str, permissions: List[str]):
        self.room = room
        self.permissions = permissions


class AccessToken:
    """
    Builder for Galene JWT Access Tokens.
    
    Usage:
        token = AccessToken("my_secret_key", "https://galene.example.com") \\
            .with_identity("username") \\
            .add_grant(VideoGrants(room="my_group", permissions=["present"])) \\
            .to_jwt()
    """
    def __init__(self, key: str, server_url: str):
        if jwt is None:
            raise ImportError("PyJWT is required for access tokens. Install it with: pip install PyJWT")
            
        self.key = key
        # Ensure server URL doesn't have a trailing slash for consistent format
        self.server_url = server_url.rstrip('/')
        self.grants: Optional[VideoGrants] = None
        self.identity: Optional[str] = None
        self.ttl: int = 3600  # Default expiration is 1 hour

    def add_grant(self, grant: VideoGrants) -> "AccessToken":
        self.grants = grant
        return self

    def with_identity(self, identity: str) -> "AccessToken":
        self.identity = identity
        return self

    def with_ttl(self, ttl_seconds: int) -> "AccessToken":
        self.ttl = ttl_seconds
        return self

    def to_jwt(self, kid: Optional[str] = None) -> str:
        if not self.grants:
            raise ValueError("VideoGrants (with room and permissions) must be provided")
        if not self.identity:
            raise ValueError("Identity (username) must be provided")

        now = int(time.time())
        
        # Galene expects the audience to be the exact HTTPS URL of the group
        # Format: https://server.com/group/groupname/
        audience = f"{self.server_url}/group/{self.grants.room}/"
        
        payload = {
            "sub": self.identity,
            "aud": audience,
            "permissions": self.grants.permissions,
            "iat": now,
            "exp": now + self.ttl
        }
        
        headers = {}
        if kid:
            headers["kid"] = kid
            
        return jwt.encode(payload, self.key, algorithm="HS256", headers=headers)


class TokenVerifier:
    """Utility to decode and verify incoming Galene tokens."""
    
    def __init__(self, key: str):
        self.key = key

    def verify(self, token: str, expected_audience: str) -> Dict[str, Any]:
        """
        Verifies the token signature, expiration, and audience.
        Returns the decoded payload.
        """
        try:
            return jwt.decode(
                token, 
                self.key, 
                algorithms=["HS256"], 
                audience=expected_audience
            )
        except jwt.PyJWTError as e:
            raise ValueError(f"Invalid token: {e}")
