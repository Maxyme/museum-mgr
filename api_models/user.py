from uuid import UUID
from pydantic import BaseModel


# Pydantic Models
class UserCreate(BaseModel):
    name: str
    email: str
    is_admin: bool = False


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    is_admin: bool | None = None


class UserRead(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    name: str
    email: str
    is_admin: bool
