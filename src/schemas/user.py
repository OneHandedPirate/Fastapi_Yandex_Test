import uuid

from pydantic import BaseModel, field_validator


class YandexUserResponseSchema(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    display_name: str
    picture: str | None
    provider: str = "yandex"


class ReadUserSchema(BaseModel):
    id: uuid.UUID
    yandex_id: str
    username: str
    first_name: str
    last_name: str
    email: str
    is_admin: bool


class CreateUserSchema(BaseModel):
    yandex_id: str
    username: str
    first_name: str
    last_name: str
    email: str
    is_admin: bool

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class UserTokenDataSchema(BaseModel):
    user_id: str


class UpdateUserSchema(BaseModel):
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
