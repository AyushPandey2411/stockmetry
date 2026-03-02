"""app/core/dependencies.py — Reusable FastAPI dependencies."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .security import decode_token
from ..models.user import User

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Decode JWT, fetch user — raises 401 if invalid."""
    token = credentials.credentials
    payload = decode_token(token)
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not payload or payload.get("type") != "access":
        raise exc
    user_id = payload.get("sub")
    if not user_id:
        raise exc
    user = db.query(User).filter(User.id == int(user_id), User.is_active == True).first()
    if not user:
        raise exc
    return user


def require_roles(*roles: str):
    """Factory returning a dependency that enforces role membership."""
    def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {' or '.join(roles)}",
            )
        return user
    return _check


# Convenience shortcuts
require_admin   = require_roles("admin")
require_manager = require_roles("admin", "manager")
require_analyst = require_roles("admin", "manager", "analyst")
