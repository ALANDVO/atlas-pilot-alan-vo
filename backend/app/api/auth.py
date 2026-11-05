"""Authentication API routes for OIDC/PKCE flow."""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional

from app.core.config import settings
from app.core.security import verify_token
from app.services.auth import auth_service, AuthState, TokenResponse


router = APIRouter(prefix="/auth", tags=["auth"])


class LoginResponse(BaseModel):
    """Login response with authorization URL."""
    auth_url: str


class CallbackRequest(BaseModel):
    """Callback request with code and state."""
    code: str
    state: str


class TokenResponseModel(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    id_token: str
    scope: str


class UserInfo(BaseModel):
    """User info from ID token."""
    sub: str
    preferred_username: str
    email: Optional[str] = None
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    realm_access: Optional[dict] = None


@router.get("/login", response_model=LoginResponse)
async def login():
    """Initiate OIDC login flow with PKCE.
    
    Redirects to Keycloak authorization endpoint with PKCE parameters.
    """
    if not settings.KEYCLOAK_URL or not settings.KEYCLOAK_REALM:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Keycloak not configured"
        )
    
    auth_url, _ = auth_service.create_authorization_url()
    return LoginResponse(auth_url=auth_url)


@router.get("/callback")
async def callback(request: Request, code: str, state: str):
    """Handle OIDC callback from Keycloak.
    
    Exchanges authorization code for tokens with PKCE verification.
    Sets HttpOnly cookies with tokens.
    """
    try:
        tokens = await auth_service.exchange_code_for_tokens(code, state)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token exchange failed: {str(e)}"
        )
    
    # Redirect to frontend with success
    # Frontend will read tokens from cookies
    frontend_url = settings.CORS_ORIGINS[0] if settings.CORS_ORIGINS else "http://localhost:5173"
    response = RedirectResponse(url=f"{frontend_url}/")
    
    # Set HttpOnly cookies for tokens
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=tokens.expires_in,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,  # 30 days
        path="/",
    )
    
    return response


@router.post("/refresh", response_model=TokenResponseModel)
async def refresh_token(request: Request, response: Response):
    """Refresh access token using refresh token cookie."""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token"
        )
    
    try:
        tokens = await auth_service.refresh_access_token(refresh_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )
    
    # Update access token cookie
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=tokens.expires_in,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
        path="/",
    )
    
    return TokenResponseModel(
        access_token=tokens.access_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in,
        refresh_token=tokens.refresh_token,
        id_token=tokens.id_token,
        scope=tokens.scope,
    )


@router.post("/logout")
async def logout(request: Request, response: Response):
    """Logout user and revoke tokens."""
    refresh_token = request.cookies.get("refresh_token")
    access_token = request.cookies.get("access_token")
    
    # Revoke at Keycloak if we have refresh token
    if refresh_token:
        try:
            await auth_service.logout(refresh_token)
        except Exception:
            pass  # Best effort
    
    # Clear cookies
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    
    # Also redirect to Keycloak logout
    frontend_url = settings.CORS_ORIGINS[0] if settings.CORS_ORIGINS else "http://localhost:5173"
    logout_url = auth_service.get_logout_url(frontend_url)
    
    return {"logout_url": logout_url}


@router.get("/me", response_model=UserInfo)
async def get_current_user(request: Request):
    """Get current user info from access token."""
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        claims = await verify_token(access_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    
    return UserInfo(
        sub=claims.get("sub", ""),
        preferred_username=claims.get("preferred_username", ""),
        email=claims.get("email"),
        name=claims.get("name"),
        given_name=claims.get("given_name"),
        family_name=claims.get("family_name"),
        realm_access=claims.get("realm_access"),
    )
