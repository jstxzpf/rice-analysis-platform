from sqlalchemy.orm import Session
from app.core.security import get_password_hash, verify_password
from app.db.models import User
from app.schemas.user import UserCreate
import secrets
from datetime import datetime, timedelta

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_password_reset_token(db: Session, user: User) -> User:
    token = secrets.token_urlsafe(32)
    expiry = datetime.utcnow() + timedelta(hours=1)
    user.reset_password_token = token
    user.reset_password_token_expiry = expiry
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_password_reset_token(db: Session, token: str) -> User | None:
    user = db.query(User).filter(User.reset_password_token == token).first()
    if not user:
        return None
    if user.reset_password_token_expiry < datetime.utcnow():
        return None
    return user

def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()

def reset_password(db: Session, user: User, new_password: str) -> User:
    user.hashed_password = get_password_hash(new_password)
    user.reset_password_token = None
    user.reset_password_token_expiry = None
    db.add(user)
    db.commit()
    db.refresh(user)
    return user