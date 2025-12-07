from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel


class User(Base):
    __tablename__ = "user"
    name: Mapped[str]
    email: Mapped[str]
    is_admin: Mapped[bool] = mapped_column(default=False)

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
