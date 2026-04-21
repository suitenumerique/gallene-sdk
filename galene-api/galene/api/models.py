import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class UserDefinition:
    """Represents a Galene user's configuration."""
    permissions: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserDefinition":
        return cls(
            permissions=data.get("permissions", [])
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "permissions": self.permissions
        }


@dataclass
class GroupDefinition:
    """
    Represents a Galene group configuration.
    Since Galene groups can have many optional configurations,
    we strongly type the common ones and store the rest in 'properties'.
    """
    description: Optional[str] = None
    contact: Optional[str] = None
    comment: Optional[str] = None
    public: Optional[bool] = None
    autolock: Optional[bool] = None
    autokick: Optional[bool] = None
    properties: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GroupDefinition":
        # Extract known properties, keep the rest in 'properties' dict
        extracted = data.copy()
        
        description = extracted.pop("description", None)
        contact = extracted.pop("contact", None)
        comment = extracted.pop("comment", None)
        public = extracted.pop("public", None)
        autolock = extracted.pop("autolock", None)
        autokick = extracted.pop("autokick", None)

        return cls(
            description=description,
            contact=contact,
            comment=comment,
            public=public,
            autolock=autolock,
            autokick=autokick,
            properties=extracted
        )

    def to_dict(self) -> Dict[str, Any]:
        result = self.properties.copy()
        if self.description is not None:
            result["description"] = self.description
        if self.contact is not None:
            result["contact"] = self.contact
        if self.comment is not None:
            result["comment"] = self.comment
        if self.public is not None:
            result["public"] = self.public
        if self.autolock is not None:
            result["autolock"] = self.autolock
        if self.autokick is not None:
            result["autokick"] = self.autokick
        
        return result


@dataclass
class StatefulToken:
    """Represents a dynamic/stateful token in Galene."""
    token_name: str
    username: str
    permissions: List[str] = field(default_factory=list)
    expires: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StatefulToken":
        return cls(
            token_name=data.get("token_name", ""),
            username=data.get("username", ""),
            permissions=data.get("permissions", []),
            expires=data.get("expires")
        )

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "token_name": self.token_name,
            "username": self.username,
            "permissions": self.permissions,
        }
        if self.expires is not None:
            result["expires"] = self.expires
        return result
