import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import File
from src.schemas.file import ReadFileSchema, CreateFileSchema


class FileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_file(self, data: CreateFileSchema) -> ReadFileSchema:
        new_file = File(user_id=data.user_id, name=data.name, path=data.path)

        self.session.add(new_file)
        await self.session.flush()
        await self.session.refresh(new_file)

        return ReadFileSchema.model_validate(new_file, from_attributes=True)

    async def get_user_files(self, user_id: uuid.UUID) -> list[ReadFileSchema]:
        stmt = select(File).where(File.user_id == user_id)
        result = (await self.session.execute(stmt)).scalars().all()

        print(result)
        return [
            ReadFileSchema.model_validate(file, from_attributes=True) for file in result
        ]
