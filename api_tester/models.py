from uuid import UUID
from pydantic import BaseModel, Field


class MuseumCreate(BaseModel):
    city: str = Field(min_length=1)
    population: int


class MuseumRead(BaseModel):
    id: UUID
    city: str = Field(min_length=1)
    population: int
