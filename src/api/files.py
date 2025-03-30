import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status, UploadFile, Form, HTTPException

from src.schemas.file import ReadFileSchema
from src.schemas.user import ReadUserSchema
from src.services.files import (
    UploadFilesService,
    get_upload_file_service,
    GetUsersFilesService,
    get_get_users_files_service,
)
from src.utils.auth import get_current_user


router = APIRouter(prefix="/files", tags=["files"])


@router.post(
    "/upload", status_code=status.HTTP_201_CREATED, response_model=ReadFileSchema
)
async def upload_file(
    file: UploadFile,
    current_user: Annotated[ReadUserSchema, Depends(get_current_user)],
    service: Annotated[UploadFilesService, Depends(get_upload_file_service)],
    name: str = Form(max_length=100),
):
    """
    Upload a file
    """
    return await service.execute(file, current_user, name)


@router.get("/my-files", response_model=list[ReadFileSchema])
async def get_my_files(
    current_user: Annotated[ReadUserSchema, Depends(get_current_user)],
    service: Annotated[GetUsersFilesService, Depends(get_get_users_files_service)],
):
    """
    Get the list of files of the current user
    """
    return await service.execute(current_user)


@router.get("/{user_id}", response_model=list[ReadFileSchema])
async def get_users_files(
    user_id: uuid.UUID,
    service: Annotated[GetUsersFilesService, Depends(get_get_users_files_service)],
    current_user: Annotated[ReadUserSchema, Depends(get_current_user)],
):
    """
    Get the list of files of the user with the given id
    """
    return await service.execute(current_user, user_id)
