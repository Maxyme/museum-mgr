from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Mapped

from api_models.base import Base


# Database Model
class Museum(Base):
    __tablename__ = "museum"
    city: Mapped[str]
    population: Mapped[int]


# Pydantic Models
class MuseumCreate(BaseModel):
    city: str
    population: int


class MuseumRead(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    city: str
    population: int
