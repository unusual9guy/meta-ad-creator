"""JWT auth dependency: verify Supabase access token and return user id."""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import SUPABASE_JWT_SECRET

security = HTTPBearer(auto_error=False)


def get_current_user_id(
    cred: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    """Verify Bearer JWT and return auth.users id (sub). Raises 401 if missing or invalid."""
    if not cred:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )
    if not SUPABASE_JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Server auth not configured",
        )
    try:
        payload = jwt.decode(
            cred.credentials,
            SUPABASE_JWT_SECRET,
            audience="authenticated",
            algorithms=["HS256"],
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return sub
