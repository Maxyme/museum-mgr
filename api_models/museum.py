from typing import Any
from uuid import UUID
from pydantic import Field, field_validator
from api_models.base import APIBase, NonEmptyString


class MuseumCreate(APIBase):
    city: NonEmptyString = Field(description="The name of the city")
    population: int = Field(
        description="The annual number of visitors to the museum",
        json_schema_extra={"gte": 0},
    )


class MuseumRead(APIBase):
    id: UUID = Field(description="The unique identifier of the museum")
    city: NonEmptyString = Field(description="The name of the city")
    population: int = Field(description="The annual number of visitors to the museum")

    @field_validator("city", mode="before")
    @classmethod
    def get_city_name(cls, v: Any) -> Any:
        if hasattr(v, "name"):
            return v.name
        return v
