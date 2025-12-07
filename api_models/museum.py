from uuid import UUID

from advanced_alchemy.base import UUIDAuditBase
from pydantic import BaseModel
from sqlalchemy.orm import Mapped


# Database Model


# Pydantic Models
class MuseumCreate(BaseModel):
    city: str
    population: int


class MuseumRead(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    city: str
    population: int
