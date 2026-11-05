"""PKCE (Proof Key for Code Exchange) utilities for OIDC flow."""
import base64
import hashlib
import secrets
from dataclasses import dataclass


@dataclass
class PKCEPair:
    """PKCE code verifier and challenge pair."""
    code_verifier: str
    code_challenge: str
    code_challenge_method: str = "S256"


def generate_pkce_pair() -> PKCEPair:
    """Generate a PKCE code verifier and challenge pair.
    
    Returns:
        PKCEPair with code_verifier (43-128 chars) and code_challenge (base64url encoded SHA256)
    """
    # Generate cryptographically random code verifier (43-128 chars)
    # Using 32 bytes = 43 chars base64url (no padding)
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
    
    # Generate code challenge: SHA256 of verifier, base64url encoded
    challenge_bytes = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(challenge_bytes).decode().rstrip("=")
    
    return PKCEPair(
        code_verifier=code_verifier,
        code_challenge=code_challenge,
        code_challenge_method="S256"
    )


def verify_pkce(code_verifier: str, code_challenge: str) -> bool:
    """Verify a PKCE code verifier against a challenge.
    
    Args:
        code_verifier: The original code verifier
        code_challenge: The challenge to verify against
        
    Returns:
        True if verification succeeds
    """
    challenge_bytes = hashlib.sha256(code_verifier.encode()).digest()
    computed_challenge = base64.urlsafe_b64encode(challenge_bytes).decode().rstrip("=")
    return secrets.compare_digest(computed_challenge, code_challenge)
