import logging
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings

logger = logging.getLogger(__name__)

security_bearer = HTTPBearer(auto_error=True)


def verify_admin_token(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
) -> bool:
    """
    Verify admin Bearer token using constant-time comparison.
    """

    token = credentials.credentials.strip()

    # Reject empty tokens
    if not token:
        logger.warning("Empty admin token received.")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Constant-time comparison
    if not secrets.compare_digest(token, settings.SECRET_KEY):

        logger.warning("Invalid admin authentication attempt.")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return True