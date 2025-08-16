import os
from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

# Get API key from environment variable, fallback to default for development
API_KEY = os.getenv("API_KEY", "your-secure-api-key")
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Simulating a user role mapping
# In production, this should be replaced with a proper user management system
USER_ROLES = {
    API_KEY: "admin",  # Admin role from environment
    "another-api-key": "user"        # Regular user role
}

def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header in USER_ROLES:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )

def has_role(required_role: str):
    def role_checker(api_key: str = Depends(get_api_key)):
        user_role = USER_ROLES.get(api_key)
        if user_role != required_role:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
    return role_checker