from datetime import datetime, timedelta, UTC
from typing import Annotated, Literal

from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.db.session import get_async_session
from src.repositories.user_repo import UserRepository
from src.schemas.auth import TokenPairResponseSchema, AccessTokenResponseSchema
from src.schemas.user import UserTokenDataSchema, ReadUserSchema
from src.core.config import Settings, get_settings


settings: Settings = get_settings()


def create_tokens(
    data: UserTokenDataSchema, is_access_only: bool = False
) -> TokenPairResponseSchema | AccessTokenResponseSchema:
    to_encode = data.model_dump()
    access_token_expire = datetime.now(UTC) + timedelta(
        minutes=settings.auth.access_token_expire_minutes
    )
    to_encode.update({"exp": access_token_expire, "type": "access"})
    access_token = jwt.encode(to_encode, settings.auth.secret_key, algorithm="HS256")

    tokens = {"access_token": access_token}

    if not is_access_only:
        refresh_token_expire = datetime.now(UTC) + timedelta(
            minutes=settings.auth.refresh_token_expire_minutes
        )
        to_encode.update({"exp": refresh_token_expire, "type": "refresh"})
        refresh_token = jwt.encode(
            to_encode, settings.auth.secret_key, algorithm="HS256"
        )
        tokens["refresh_token"] = refresh_token

        return TokenPairResponseSchema.model_validate(tokens)

    return AccessTokenResponseSchema.model_validate(tokens)


def verify_token(
    token: str, token_type: Literal["access", "refresh"] = "access"
) -> UserTokenDataSchema | None:
    try:
        payload = jwt.decode(token, settings.auth.secret_key, algorithms="HS256")
        _type = payload.get("type")

        if not _type or token_type != _type:
            return None

        return UserTokenDataSchema.model_validate(payload)
    except JWTError:
        return None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_async_session),
) -> ReadUserSchema:
    user_token_data: UserTokenDataSchema | None = verify_token(token)

    if not user_token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user_repository = UserRepository(session)
    user: ReadUserSchema | None = await user_repository.get_user_by_id(
        user_token_data.user_id
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return ReadUserSchema.model_validate(user)
