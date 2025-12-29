from uuid import UUID
from pydantic import Field
from api_models.base import APIBase


class MuseumCreate(APIBase):
    city_id: UUID = Field(
        description="The unique identifier of the city where the museum is located"
    )
    population: int = Field(
        description="The annual number of visitors to the museum", gte=0
    )


class MuseumRead(APIBase):
    id: UUID = Field(description="The unique identifier of the museum")
    city_id: UUID = Field(
        description="The unique identifier of the city where the museum is located"
    )
    population: int = Field(description="The annual number of visitors to the museum")
