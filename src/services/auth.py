from typing import Annotated

from fastapi import requests, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Settings, get_settings
from src.db.session import get_async_session
from src.repositories.user_repo import UserRepository
from src.schemas.auth import TokenPairResponseSchema
from src.schemas.user import (
    YandexUserResponseSchema,
    ReadUserSchema,
    CreateUserSchema,
    UserTokenDataSchema,
)
from src.utils.auth import create_tokens


class AuthService:
    def __init__(
        self, settings: Settings, request: requests.Request, db_session: AsyncSession
    ):
        self.sso = settings.yandex.get_yandex_sso
        self.request = request
        self.settings = settings
        self.db_session = db_session

    async def execute(self) -> TokenPairResponseSchema:
        yandex_user: YandexUserResponseSchema = await self._verify_user()
        user_repository = UserRepository(self.db_session)

        user: ReadUserSchema | None = await user_repository.get_user_by_yandex_id(
            yandex_user.id
        )

        if not user:
            new_user_data = CreateUserSchema(
                yandex_id=yandex_user.id,
                email=yandex_user.email,
                username=yandex_user.display_name,
                first_name=yandex_user.first_name,
                last_name=yandex_user.last_name,
                is_admin=yandex_user.email.lower() in self.settings.admin_emails,
            )
            user: ReadUserSchema = await user_repository.create_user(new_user_data)

        return create_tokens(data=UserTokenDataSchema(user_id=str(user.id)))

    async def _verify_user(self):
        try:
            async with self.sso:
                user_data = dict(await self.sso.verify_and_process(self.request))
                return YandexUserResponseSchema(**user_data)

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error verifying user: {e}")


def get_auth_service(
    request: requests.Request,
    settings: Annotated[Settings, Depends(get_settings)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
) -> AuthService:
    return AuthService(settings, request, db_session)
