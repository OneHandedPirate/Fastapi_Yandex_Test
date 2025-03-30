import uuid

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User
from src.schemas.user import ReadUserSchema, CreateUserSchema, UpdateUserSchema


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_yandex_id(self, yandex_id: str) -> ReadUserSchema | None:
        stmt = select(User).where(User.yandex_id == yandex_id)

        user: User | None = (await self.session.execute(stmt)).scalar_one_or_none()

        if not user:
            return None

        return ReadUserSchema.model_validate(user, from_attributes=True)

    async def get_user_by_id(self, user_id: str | uuid.UUID) -> ReadUserSchema | None:
        if isinstance(user_id, str):
            stmt = select(User).where(User.id == uuid.UUID(user_id))
        else:
            stmt = select(User).where(User.id == user_id)

        user: User | None = (await self.session.execute(stmt)).scalar_one_or_none()

        if not user:
            return None
        else:
            return ReadUserSchema.model_validate(user, from_attributes=True)

    async def create_user(self, data: CreateUserSchema) -> ReadUserSchema:
        new_user = User(
            yandex_id=data.yandex_id,
            username=data.username,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            is_admin=data.is_admin,
        )

        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

        return ReadUserSchema.model_validate(new_user, from_attributes=True)

    async def update_user(
        self, user_id: uuid.UUID, data: UpdateUserSchema
    ) -> ReadUserSchema:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(data.model_dump(exclude_unset=True))
            .returning(User)
        )

        user: User = (await self.session.execute(stmt)).scalar_one()
        await self.session.commit()

        return ReadUserSchema.model_validate(user, from_attributes=True)

    async def delete_user(self, user_id: uuid.UUID) -> None:
        stmt = delete(User).where(User.id == user_id)

        await self.session.execute(stmt)
        await self.session.commit()
