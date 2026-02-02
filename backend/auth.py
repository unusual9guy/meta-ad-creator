"""Auth dependency: verify Supabase access token via Supabase Auth and return user id."""

import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

security = HTTPBearer(auto_error=False)


def get_current_user_id(
    cred: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    """
    Verify Bearer JWT by calling Supabase Auth and return auth.users id.

    This avoids having to know the exact JWT signing algorithm; Supabase
    validates the token for us using the project's configuration.
    """
    if not cred:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Server auth not configured",
        )

    try:
        resp = requests.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {cred.credentials}",
                "apikey": SUPABASE_SERVICE_ROLE_KEY,
            },
            timeout=5,
        )
    except requests.RequestException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to contact Supabase Auth",
        )

    if resp.status_code != 200:
        # Supabase will return 401/403 for invalid or expired tokens.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    data = resp.json()
    user_id = data.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return user_id
