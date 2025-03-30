import io
import uuid
from typing import Annotated

import aiofiles
import aiofiles.os
import magic
from fastapi import UploadFile, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Settings, BASE_DIR, get_settings
from src.db.session import get_async_session
from src.repositories.user_repo import UserRepository
from src.schemas.file import CreateFileSchema, ReadFileSchema
from src.schemas.user import ReadUserSchema
from src.repositories.file_repo import FileRepository


class UploadFilesService:
    def __init__(self, settings: Settings, db_session: AsyncSession):
        self.settings = settings
        self.db_session = db_session

    async def execute(
        self, file: UploadFile, current_user: ReadUserSchema, name: str
    ) -> ReadFileSchema:
        upload_dir = BASE_DIR / "files" / str(current_user.id)
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_ext = None
        if "." in file.filename:
            file_ext = file.filename.split(".")[-1]

        safe_filename = f"{uuid.uuid4()}{'.' + file_ext if file_ext else ''}"
        upload_path = upload_dir / safe_filename

        file_content: bytes = await file.read(1024)

        mime: magic.Magic = magic.Magic(mime=True)
        file_type: str = mime.from_buffer(file_content)

        if file_type not in self.settings.files.allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="File type not allowed"
            )

        if file.size > self.settings.files.max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="File size is too large"
            )

        try:
            file_stream = io.BytesIO(file_content)

            file_repo = FileRepository(self.db_session)

            new_file: ReadFileSchema = await file_repo.create_file(
                CreateFileSchema(
                    user_id=current_user.id, name=name, path=str(upload_path)
                )
            )

            async with aiofiles.open(upload_path, "wb") as buffer:
                await buffer.write(file_stream.getvalue())

                while chunk := await file.read(1024):
                    await buffer.write(chunk)

        except Exception:
            await self.db_session.rollback()
            if aiofiles.os.path.exists(upload_path):
                await aiofiles.os.remove(upload_path)

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Something went wrong while uploading file",
            )
        else:
            await self.db_session.commit()
            return new_file


class GetUsersFilesService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def execute(
        self, current_user: ReadUserSchema, user_id: uuid.UUID = None
    ) -> list[ReadFileSchema]:
        file_repo = FileRepository(self.db_session)

        _id = user_id or current_user.id

        if user_id:
            user_repo = UserRepository(self.db_session)
            if not await user_repo.get_user_by_id(_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

        if not current_user.is_admin and current_user.id != _id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to get other user's files",
            )

        return await file_repo.get_user_files(_id)


def get_upload_file_service(
    settings: Annotated[Settings, Depends(get_settings)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UploadFilesService:
    return UploadFilesService(settings=settings, db_session=db_session)


def get_get_users_files_service(
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
) -> GetUsersFilesService:
    return GetUsersFilesService(db_session=db_session)
