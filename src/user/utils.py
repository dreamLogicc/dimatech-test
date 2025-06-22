import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from datetime import datetime, timedelta

from config import SECRET_KEY, ALGORITHM
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session

from user.models import user

from user.schemas import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


async def get_user(email: str, session: AsyncSession) -> dict | None:
    query = select(user).where(user.c.email == email)
    result = await session.execute(query)
    user_row = result.fetchone()
    return dict(user_row._mapping) if user_row else None


async def authenticate_user(email: str, password: str, session: AsyncSession) -> dict | bool:
    user = await get_user(email, session)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_async_session)
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user(email, session)
    if user is None:
        raise credentials_exception

    user.pop('hashed_password')

    return user


async def verify_admin(
        current_user: User = Depends(get_current_user)
) -> User:
    if current_user['role_id'] != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Need Admin role"
        )
    return current_user
