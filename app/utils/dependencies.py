from fastapi import Depends, HTTPException, status
from app.utils.security import get_current_active_user
from app.models.user import User, UserRole

def get_current_admin(current_user: User = Depends(get_current_active_user)):
    """Проверка, что текущий пользователь является администратором"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user