"""Authentication dependencies for FastAPI routes."""
from fastapi import Depends, HTTPException, Request, status
from typing import Optional, List

from app.core.security.jwt import verify_token


class CurrentUser:
    """Current authenticated user from JWT claims."""
    
    def __init__(self, claims: dict):
        self.claims = claims
        self.sub = claims.get("sub", "")
        self.preferred_username = claims.get("preferred_username", "")
        self.email = claims.get("email")
        self.name = claims.get("name")
        self.given_name = claims.get("given_name")
        self.family_name = claims.get("family_name")
        self.realm_access = claims.get("realm_access", {})
        self.roles = self.realm_access.get("roles", [])
    
    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return role in self.roles
    
    def has_any_role(self, roles: List[str]) -> bool:
        """Check if user has any of the specified roles."""
        return any(role in self.roles for role in roles)


async def _get_token_from_request(request: Request) -> Optional[str]:
    """Extract access token from cookies or Authorization header."""
    # First try cookie (production flow)
    access_token = request.cookies.get("access_token")
    if access_token:
        return access_token
    
    # Fall back to Authorization header
    authorization: str = request.headers.get("Authorization", "")
    if authorization.startswith("Bearer "):
        return authorization[7:]
    
    return None


async def get_current_user(request: Request) -> CurrentUser:
    """Get current user from access token (cookie or Authorization header)."""
    access_token = await _get_token_from_request(request)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        claims = await verify_token(access_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return CurrentUser(claims)


async def get_optional_user(request: Request) -> Optional[CurrentUser]:
    """Get current user if authenticated, otherwise None.
    
    Supports both cookie-based and Authorization header-based tokens.
    """
    access_token = await _get_token_from_request(request)
    if not access_token:
        return None
    
    try:
        claims = await verify_token(access_token)
        return CurrentUser(claims)
    except Exception:
        return None


def require_role(role: str):
    """Dependency factory for requiring a specific role."""
    async def role_checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not user.has_role(role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {role}",
            )
        return user
    return role_checker


def require_any_role(roles: List[str]):
    """Dependency factory for requiring any of the specified roles."""
    async def role_checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not user.has_any_role(roles):
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Required one of roles: {roles}",
        )
        return user
    return role_checker
