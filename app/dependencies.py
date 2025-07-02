"""Dependency utilities for API key authentication and role checking."""

from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

API_KEY = "your-secure-api-key"
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Simulating a user role mapping
USER_ROLES = {
    "your-secure-api-key": "admin",  # Admin role
    "another-api-key": "user"        # Regular user role
}

def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    """Validate the provided API key and return it if valid."""
    if api_key_header in USER_ROLES:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )

def has_role(required_role: str):
    """Return a dependency that ensures the authenticated user has ``required_role``."""

    def role_checker(api_key: str = Depends(get_api_key)):
        user_role = USER_ROLES.get(api_key)
        if user_role != required_role:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )

    return role_checker