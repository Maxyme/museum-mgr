from uuid import UUID
from pydantic import BaseModel

class MuseumCreate(BaseModel):
    city: str
    population: int

class MuseumRead(BaseModel):
    id: UUID
    city: str
    population: int
