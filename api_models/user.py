from uuid import UUID
from pydantic import Field, EmailStr
from api_models.base import APIBase, NonEmptyString


class ApiUserIn(APIBase):
    name: NonEmptyString = Field(description="The name of the user")
    email: EmailStr = Field(description="The email address of the user")
    is_admin: bool = Field(
        default=False, description="Whether the user has administrative privileges"
    )


class ApiUserOut(ApiUserIn):
    id: UUID = Field(description="The unique identifier of the user")
