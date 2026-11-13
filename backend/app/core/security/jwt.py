"""JWT token handling for OIDC authentication."""
import time
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import httpx
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError

from app.core.config import settings


# In-memory JWKS cache
_jwks_cache: Optional[Dict[str, Any]] = None
_jwks_cache_time: float = 0
_JWKS_CACHE_TTL = 3600  # 1 hour


async def get_jwks() -> Dict[str, Any]:
    """Fetch and cache JWKS from Keycloak.
    
    Returns:
        JWKS dictionary with keys
    """
    global _jwks_cache, _jwks_cache_time
    
    now = time.time()
    if _jwks_cache and (now - _jwks_cache_time) < _JWKS_CACHE_TTL:
        return _jwks_cache
    
    if not settings.KEYCLOAK_URL or not settings.KEYCLOAK_REALM:
        raise ValueError("Keycloak URL and realm must be configured")
    
    jwks_url = urljoin(f"{settings.KEYCLOAK_URL}/", f"realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/certs")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(jwks_url)
        response.raise_for_status()
        _jwks_cache = response.json()
        _jwks_cache_time = now
        return _jwks_cache


def get_signing_key(token: str, jwks: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the signing key from JWKS matching the token's kid.
    
    Args:
        token: JWT token
        jwks: JWKS dictionary
        
    Returns:
        Signing key dictionary
        
    Raises:
        JWTError: If no matching key found
    """
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    
    if not kid:
        raise JWTError("Token missing kid header")
    
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    
    raise JWTError(f"No matching key found for kid: {kid}")


async def verify_token(token: str) -> Dict[str, Any]:
    """Verify a JWT access token.
    
    Supports both Keycloak RS256 tokens (with kid) and internal HS256 tokens.
    
    Args:
        token: JWT access token
        
    Returns:
        Decoded token claims
        
    Raises:
        JWTError: If token is invalid
        ExpiredSignatureError: If token is expired
        JWTClaimsError: If claims validation fails
    """
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    alg = header.get("alg")
    
    if kid:
        # Keycloak token (RS256)
        jwks = await get_jwks()
        signing_key = get_signing_key(token, jwks)
        # Verify with Keycloak audience/issuer
        claims = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=settings.KEYCLOAK_CLIENT_ID,
            issuer=f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}",
            options={
                "verify_aud": True,
                "verify_iss": True,
                "verify_exp": True,
            }
        )
    elif alg == "HS256":
        # Internal token (HS256)
        claims = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
            options={
                "verify_exp": True,
            }
        )
    else:
        raise JWTError(f"Unsupported token algorithm: {alg}")
    
    return claims
def decode_token(token: str) -> Dict[str, Any]:
    """Decode a JWT token without verification (for debugging).
    
    Args:
        token: JWT token
        
    Returns:
        Decoded claims (unverified)
    """
    return jwt.get_unverified_claims(token)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
    """Create a JWT access token for internal use.
    
    Args:
        data: Claims to include
        expires_delta: Expiration in minutes
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    expire = time.time() + (expires_delta or settings.ACCESS_TOKEN_EXPIRE_MINUTES) * 60
    to_encode.update({"exp": expire, "iat": time.time()})
    
    # For internal tokens, we use HS256 with SECRET_KEY
    # In production with Keycloak, tokens are issued by Keycloak (RS256)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
