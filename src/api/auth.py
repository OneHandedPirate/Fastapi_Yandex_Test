from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_sso.sso.yandex import YandexSSO

from src.core.config import Settings, get_settings
from src.schemas.auth import (
    TokenPairResponseSchema,
    RefreshTokenSchema,
    AccessTokenResponseSchema,
)
from src.schemas.user import ReadUserSchema
from src.services.auth import AuthService, get_auth_service
from src.services.refresh import RefreshTokenService, get_refresh_token_service
from src.utils.auth import get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login(settings: Annotated[Settings, Depends(get_settings)]):
    """Login via Yandex"""
    sso: YandexSSO = settings.yandex.get_yandex_sso

    async with sso:
        return await sso.get_login_redirect()


@router.get("/callback", response_model=TokenPairResponseSchema)
async def callback(auth_service: Annotated[AuthService, Depends(get_auth_service)]):
    """
    Callback from Yandex
    """
    return await auth_service.execute()


@router.post("/refresh", response_model=AccessTokenResponseSchema)
async def refresh(
    data: RefreshTokenSchema,
    refresh_token_service: Annotated[
        RefreshTokenService, Depends(get_refresh_token_service)
    ],
):
    """
    Refresh access token via refresh token
    """
    return await refresh_token_service.execute(data)
