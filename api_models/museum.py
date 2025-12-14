from uuid import UUID
from typing import Any

from pydantic import BaseModel, field_validator


# Pydantic Models
class MuseumCreate(BaseModel):
    city: str
    population: int


class MuseumRead(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    city: str
    population: int

    @field_validator("city", mode="before")
    @classmethod
    def extract_city_name(cls, v: Any) -> str:
        if hasattr(v, "name"):
            return v.name
        return str(v)
