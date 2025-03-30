import uuid

from pydantic import BaseModel


class ReadFileSchema(BaseModel):
    id: uuid.UUID
    name: str
    path: str


class CreateFileSchema(BaseModel):
    user_id: uuid.UUID
    name: str
    path: str
