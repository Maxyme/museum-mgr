from uuid import UUID
from sqlalchemy.orm import Mapped
from pydantic import BaseModel

from api_models.base import Base

# Database Model
class User(Base):
    __tablename__ = "user"
    name: Mapped[str]
    email: Mapped[str]

# Pydantic Models
class UserCreate(BaseModel):
    name: str
    email: str

class UserRead(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    name: str
    email: str
