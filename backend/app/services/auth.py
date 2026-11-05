"""Authentication service for OIDC/PKCE flow with Keycloak."""
import secrets
from dataclasses import dataclass
from urllib.parse import urlencode, urljoin

import httpx

from app.core.config import settings
from app.core.security.pkce import PKCEPair, generate_pkce_pair


@dataclass
class AuthState:
    """OIDC authorization state with PKCE."""
    state: str
    pkce: PKCEPair
    nonce: str


@dataclass
class TokenResponse:
    """Token response from Keycloak."""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    id_token: str
    scope: str


class AuthService:
    """Service for handling OIDC authentication flow with Keycloak."""
    
    def __init__(self):
        self._pending_states: dict[str, AuthState] = {}
    
    def create_authorization_url(self) -> tuple[str, AuthState]:
        """Create the Keycloak authorization URL with PKCE.
        
        Returns:
            Tuple of (authorization_url, auth_state)
        """
        # Generate state and nonce for CSRF protection
        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)
        
        # Generate PKCE pair
        pkce = generate_pkce_pair()
        
        auth_state = AuthState(state=state, pkce=pkce, nonce=nonce)
        self._pending_states[state] = auth_state
        
        # Build authorization URL
        base_url = f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/auth"
        
        params = {
            "client_id": settings.KEYCLOAK_CLIENT_ID,
            "response_type": "code",
            "scope": "openid profile email roles",
            "redirect_uri": settings.KEYCLOAK_REDIRECT_URI,
            "state": state,
            "nonce": nonce,
            "code_challenge": pkce.code_challenge,
            "code_challenge_method": pkce.code_challenge_method,
        }
        
        auth_url = f"{base_url}?{urlencode(params)}"
        return auth_url, auth_state
    
    async def exchange_code_for_tokens(self, code: str, state: str) -> TokenResponse:
        """Exchange authorization code for tokens with PKCE verification.
        
        Args:
            code: Authorization code from Keycloak callback
            state: State parameter from callback
            
        Returns:
            TokenResponse with access token, ID token, refresh token
            
        Raises:
            ValueError: If state is invalid or PKCE verification fails
            httpx.HTTPError: If token exchange fails
        """
        # Verify state
        auth_state = self._pending_states.pop(state, None)
        if not auth_state:
            raise ValueError("Invalid or expired state")
        
        # Exchange code for tokens
        token_url = f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token"
        
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.KEYCLOAK_CLIENT_ID,
            "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.KEYCLOAK_REDIRECT_URI,
            "code_verifier": auth_state.pkce.code_verifier,
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
        
        return TokenResponse(
            access_token=token_data["access_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            refresh_token=token_data["refresh_token"],
            id_token=token_data["id_token"],
            scope=token_data.get("scope", ""),
        )
    
    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Refresh an access token using refresh token.
        
        Args:
            refresh_token: Refresh token from previous authentication
            
        Returns:
            New TokenResponse
        """
        token_url = f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token"
        
        data = {
            "grant_type": "refresh_token",
            "client_id": settings.KEYCLOAK_CLIENT_ID,
            "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
            "refresh_token": refresh_token,
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
        
        return TokenResponse(
            access_token=token_data["access_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            refresh_token=token_data.get("refresh_token", refresh_token),
            id_token=token_data.get("id_token", ""),
            scope=token_data.get("scope", ""),
        )
    
    async def logout(self, refresh_token: str) -> None:
        """Logout user at Keycloak (revoke refresh token).
        
        Args:
            refresh_token: Refresh token to revoke
        """
        logout_url = f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/logout"
        
        data = {
            "client_id": settings.KEYCLOAK_CLIENT_ID,
            "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
            "refresh_token": refresh_token,
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(logout_url, data=data)
    
    def get_logout_url(self, post_logout_redirect_uri: str) -> str:
        """Get Keycloak logout URL.
        
        Args:
            post_logout_redirect_uri: URI to redirect after logout
            
        Returns:
            Logout URL
        """
        base_url = f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/logout"
        params = {
            "client_id": settings.KEYCLOAK_CLIENT_ID,
            "post_logout_redirect_uri": post_logout_redirect_uri,
        }
        return f"{base_url}?{urlencode(params)}"


# Global auth service instance
auth_service = AuthService()
