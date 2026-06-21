from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import User

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
_oauth2 = OAuth2PasswordBearer(tokenUrl="/v1/auth/token")


def hash_password(plain: str) -> str:
    return _pwd.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd.verify(plain, hashed)


def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode(
        {"sub": username, "exp": expire},
        settings.api_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def get_current_user(
    token: str = Depends(_oauth2),
    db: Session = Depends(get_db),
) -> User:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.api_secret_key, algorithms=[settings.jwt_algorithm]
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise exc
    except JWTError:
        raise exc

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise exc
    return user
