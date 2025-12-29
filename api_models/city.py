from uuid import UUID
from pydantic import Field
from api_models.base import APIBase, NonEmptyString


class CityCreate(APIBase):
    name: NonEmptyString = Field(description="The name of the city")
    population: int = Field(
        description="The population of the city", json_schema_extra={"gte": 0}
    )


class CityRead(APIBase):
    id: UUID = Field(description="The unique identifier of the city")
    name: NonEmptyString = Field(description="The name of the city")
    population: int = Field(description="The population of the city")
