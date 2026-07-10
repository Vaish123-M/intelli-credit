from typing import List
from fastapi import Depends, HTTPException, status
from app.auth.jwt_handler import get_current_user
from app.auth.models import TokenData, UserRole


async def get_current_active_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Get current active user."""
    return current_user


def require_role(allowed_roles: List[UserRole]):
    """Dependency to require specific user roles."""
    async def role_checker(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{current_user.role}' not authorized. Required: {[r.value for r in allowed_roles]}",
            )
        return current_user
    return role_checker
