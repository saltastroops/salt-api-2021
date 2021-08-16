from typing import Dict, Any, Optional, cast
from datetime import datetime, timedelta, date

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.repository.user_repository import UserRepository
from saltapi.service.authentication import AccessToken
from saltapi.service.user import User
from jose import jwt, JWTError

from saltapi.settings import Settings

ALGORITHM = "HS256"
ACCESS_TOKEN_LIFETIME_HOURS = 7 * 24
SECRET_KEY = Settings().secret_key
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthenticationService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def access_token(self, user: User) -> AccessToken:
        """Generate an authentication token."""
        token_expires = timedelta(hours=ACCESS_TOKEN_LIFETIME_HOURS)
        token = self.jwt_token(
            payload={"sub": user.username},
            expires_delta=token_expires,
        )

        return AccessToken(
            access_token=token,
            token_type="bearer",
            expires_at=date.today() + timedelta(hours=ACCESS_TOKEN_LIFETIME_HOURS),
        )  # nosec

    @staticmethod
    def jwt_token(
        payload: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
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
        user = self.user_repository.find_user_with_username_and_password(
            username, password
        )
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


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    with UnitOfWork() as unit_of_work:
        try:
            user_repository = UserRepository(unit_of_work.connection)
            authentication_repository = AuthenticationService(user_repository)

            return authentication_repository.validate_auth_token(token)
        except:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate token.",
                headers={"WWW-Authenticate": "Bearer"},
            )