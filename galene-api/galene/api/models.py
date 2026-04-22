from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class UserDefinition(BaseModel):
    """Represents a Galene user's configuration.
    permissions can be 'observe', 'present', 'op', 'admin', 'message', 'caption'
    for now we consider that each user only have 1 permission at a time
    """

    permissions: Optional[str] = 'observe'



class GroupDefinition(BaseModel):
    """
    Represents a Galene group configuration.
    Galene groups can have many optional configurations. Unknown fields 
    are captured as extra properties (accessible via `.model_extra`).
    """
    model_config = ConfigDict(extra='allow')

    description: Optional[str] = None
    contact: Optional[str] = None
    comment: Optional[str] = None
    public: Optional[bool] = None
    autolock: Optional[bool] = None
    autokick: Optional[bool] = None


class StatefulToken(BaseModel):
    """Represents a dynamic/stateful token in Galene."""
    token_name: str
    username: str
    permissions: List[str] = Field(default_factory=list)
    expires: Optional[str] = None
