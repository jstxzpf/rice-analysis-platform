from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import oauth2_scheme
from app.crud import crud_user
from app.db.base import get_db
from app.db.models import User

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    # This is a simplified placeholder. In a real app, you'd decode the JWT token.
    # For now, we'll just use a dummy user or a simple lookup.
    # Let's assume the token is the username for simplicity in this mock-up.
    user = crud_user.get_user_by_username(db, username=token) # Simplified: token IS the username
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user

