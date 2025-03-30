import uuid
import datetime as dt

from sqlalchemy import MetaData, DateTime, ForeignKey
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy_utils import UUIDType

from src.core.config import get_settings, Settings


settings: Settings = get_settings()

metadata = MetaData(naming_convention=settings.db.naming_convention)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(binary=False),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.now(dt.UTC),
        server_default=func.now(),
    )

    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.now(dt.UTC),
        server_default=func.now(),
        onupdate=lambda: dt.datetime.now(dt.UTC),
    )

    metadata = metadata


class User(Base):
    __tablename__ = "users"

    yandex_id: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    username: Mapped[str] = mapped_column(nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    is_admin: Mapped[bool] = mapped_column(nullable=False)

    files: Mapped[list["File"]] = relationship(back_populates="user")


class File(Base):
    __tablename__ = "files"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(binary=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(nullable=False)
    path: Mapped[str] = mapped_column(nullable=False)

    user: Mapped[User] = relationship(back_populates="files")
