"""
API Call model for network endpoint representation.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class APICall(BaseModel):
    """
    API endpoint representation

    Captured from network observations or static analysis
    """
    name: str = Field(..., description="API call identifier")
    endpoint: str = Field(..., description="API endpoint path")
    method: str = Field(..., description="HTTP method")
    request_schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="Request/Response schema",
        alias="schema"  # Backward compatibility
    )
    responses: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Observed responses"
    )
    triggers_state_change: Optional[str] = Field(
        None,
        description="State machine event this API triggers"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "auth_login",
                "endpoint": "/api/v1/auth/login",
                "method": "POST",
                "request_schema": {
                    "username": "string",
                    "password": "string"
                },
                "triggers_state_change": "login_success"
            }
        },
        "populate_by_name": True  # Allow using 'schema' alias
    }
