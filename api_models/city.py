from uuid import UUID
from pydantic import Field
from api_models.base import APIBase


class CityCreate(APIBase):
    name: str = Field(description="The name of the city", min_length=1)
    population: int = Field(description="The population of the city", gte=0)


class CityRead(APIBase):
    id: UUID = Field(description="The unique identifier of the city")
    name: str = Field(description="The name of the city")
    population: int = Field(description="The population of the city")
