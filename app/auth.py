import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings

bearer_scheme = HTTPBearer()

# Supabase publishes its current signing keys here — no secret needed, this is
# a public endpoint. PyJWKClient fetches and caches the right key automatically,
# matched by the token's "kid" header, and handles key rotation for us.
_jwks_url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
_jwk_client = jwt.PyJWKClient(_jwks_url)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """Verifies the Supabase-issued JWT sent by the Android app and returns its claims.
    The Android app gets this token from Supabase Auth after login/register."""
    token = credentials.credentials
    try:
        signing_key = _jwk_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return payload  # payload["sub"] is the Supabase user id (uuid)
