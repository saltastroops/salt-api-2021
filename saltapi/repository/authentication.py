from typing import Dict, Any, Optional, cast
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.engine import Connection
from starlette import status

from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.repository.user_repository import UserRepository
from saltapi.service.authenticate import AccessToken
from saltapi.service.user import User
from jose import jwt, JWTError


ALGORITHM = "HS256"
ACCESS_TOKEN_LIFETIME_HOURS = 7 * 24
SECRET_KEY = ""
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthenticationRepository:
    def __init__(self, connection: Connection, user_repository: UserRepository) -> None:
        self.connection = connection
        self.user_repository = user_repository

    def access_token(self, user: User) -> AccessToken:
        """Generate an authentication token."""
        token_expires = timedelta(hours=ACCESS_TOKEN_LIFETIME_HOURS)
        token = self.jwt_token(
            payload={"sub": user.username},
            expires_delta=token_expires,
        )

        return AccessToken(access_token=token, token_type="bearer")  # nosec

    @staticmethod
    def jwt_token(payload: Dict[str, Any],
                  expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT token."""
        to_encode = payload.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_LIFETIME_HOURS)
        to_encode["exp"] = expire
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return cast(str, encoded_jwt)

    def authenticate_user(self, username: str, password: str) -> User:
        user = self.user_repository.find_user_with_username_and_password(username, password)
        if not user:
            raise ValueError("User not found or password doesn't match.")
        return user

    def validate_auth_token(self, token: str) -> User:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload:
            raise JWTError("Token failed to decode.")
        user = self.user_repository.get(payload["sub"])
        if not user:
            raise ValueError("Token not valid.")
        return user


def is_user_admin_or_salt_astronomer(token: str = Depends(oauth2_scheme)):
    with UnitOfWork() as unit_of_work:
        try:
            user_repository = UserRepository(unit_of_work.connection)
            authentication_repository = AuthenticationRepository(
                unit_of_work.connection,
                user_repository)

            user = authentication_repository.validate_auth_token(token)
            if user_repository.is_administrator(user.username):
                return True
            if user_repository.is_salt_astronomer(user.username):
                return True
            return False
        except:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
