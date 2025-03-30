import uuid
from typing import Annotated

import aiofiles.os
from fastapi import HTTPException, status
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import BASE_DIR
from src.db.session import get_async_session
from src.repositories.user_repo import UserRepository
from src.schemas.user import ReadUserSchema, UpdateUserSchema


class BaseUserService:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session
        self.user_repository = UserRepository(db_session)

    async def _get_user_or_404(self, user_id: uuid.UUID) -> ReadUserSchema:
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    @staticmethod
    def _check_admin_permissions(current_user: ReadUserSchema) -> None:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission for this action",
            )


class RetrieveUserService(BaseUserService):
    async def execute(self, user_id: uuid.UUID) -> ReadUserSchema:
        return await self._get_user_or_404(user_id)


class UpdateUserService(BaseUserService):
    async def execute(
        self, user_id: uuid.UUID, data: UpdateUserSchema, current_user: ReadUserSchema
    ) -> ReadUserSchema:
        user = await self._get_user_or_404(user_id)

        if user.id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this user",
            )

        return await self.user_repository.update_user(user_id, data)


class DeleteUserService(BaseUserService):
    async def execute(self, user_id: uuid.UUID, current_user: ReadUserSchema) -> None:
        self._check_admin_permissions(current_user)

        user = await self._get_user_or_404(user_id)

        # if user.is_admin:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="You can't delete superusers",
        #     )

        users_file_path = BASE_DIR / "files" / str(user_id)

        if await aiofiles.os.path.exists(users_file_path):
            for file in await aiofiles.os.scandir(users_file_path):
                if file.is_file():
                    await aiofiles.os.remove(file.path)
            await aiofiles.os.rmdir(users_file_path)

        await self.user_repository.delete_user(user_id)


def get_service(service_class):
    def _get_service(
        db_session: Annotated[AsyncSession, Depends(get_async_session)],
    ) -> service_class:
        return service_class(db_session=db_session)

    return _get_service


get_retrieve_user_service = get_service(RetrieveUserService)
get_update_user_service = get_service(UpdateUserService)
get_delete_user_service = get_service(DeleteUserService)
