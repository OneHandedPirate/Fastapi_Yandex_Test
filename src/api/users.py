import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.schemas.user import ReadUserSchema, UpdateUserSchema
from src.services.users import (
    get_retrieve_user_service,
    RetrieveUserService,
    UpdateUserService,
    get_update_user_service,
    get_delete_user_service,
    DeleteUserService,
)
from src.utils.auth import get_current_user


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/my-info", response_model=ReadUserSchema)
async def get_my_info(
    current_user: Annotated[ReadUserSchema, Depends(get_current_user)],
):
    """
    Get current user info
    """
    return current_user


@router.get("/{user_id}", response_model=ReadUserSchema)
async def get_user(
    user_id: uuid.UUID,
    service: Annotated[RetrieveUserService, Depends(get_retrieve_user_service)],
    current_user: Annotated[ReadUserSchema, Depends(get_current_user)],
) -> ReadUserSchema:
    """
    Get user info
    """
    return await service.execute(user_id)


@router.patch("/{user_id}", response_model=ReadUserSchema)
async def update_user(
    user_id: uuid.UUID,
    data: UpdateUserSchema,
    service: Annotated[UpdateUserService, Depends(get_update_user_service)],
    current_user: Annotated[ReadUserSchema, Depends(get_current_user)],
) -> ReadUserSchema:
    """
    Update user info
    """
    return await service.execute(user_id, data, current_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    service: Annotated[DeleteUserService, Depends(get_delete_user_service)],
    current_user: Annotated[ReadUserSchema, Depends(get_current_user)],
) -> None:
    """
    Delete user
    """
    return await service.execute(user_id, current_user)
