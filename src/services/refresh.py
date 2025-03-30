from typing import Annotated

from fastapi import HTTPException, status
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.repositories.user_repo import UserRepository
from src.schemas.auth import RefreshTokenSchema, AccessTokenResponseSchema
from src.schemas.user import UserTokenDataSchema, ReadUserSchema
from src.utils.auth import verify_token, create_tokens


class RefreshTokenService:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def execute(self, data: RefreshTokenSchema) -> AccessTokenResponseSchema:
        user_repository: UserRepository = UserRepository(session=self.db_session)

        user_token_data: UserTokenDataSchema | None = verify_token(
            data.refresh_token, token_type="refresh"
        )

        if not user_token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        user: ReadUserSchema | None = await user_repository.get_user_by_id(
            user_token_data.user_id
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return create_tokens(user_token_data, is_access_only=True)


def get_refresh_token_service(
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
) -> RefreshTokenService:
    return RefreshTokenService(db_session)
