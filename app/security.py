import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

security_bearer = HTTPBearer()

def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security_bearer)):
    """
    Validates token securely via constant-time verification.
    Prevents standard execution timing exploitation frameworks.
    """
    token = credentials.credentials
    # Use secrets.compare_digest to defend against timing side-channel attacks
    if not secrets.compare_digest(token, settings.SECRET_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access Denied: Invalid Admin Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True
