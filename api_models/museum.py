from uuid import UUID

from pydantic import BaseModel


# Pydantic Models
class MuseumCreate(BaseModel):
    city: str
    population: int


class MuseumRead(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    city: str
    population: int
