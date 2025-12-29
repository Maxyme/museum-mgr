from uuid import UUID
from pydantic import Field, EmailStr
from api_models.base import APIBase


class ApiUserIn(APIBase):
    name: str = Field(description="The name of the user", min_length=1)
    email: EmailStr = Field(description="The email address of the user")
    is_admin: bool = Field(
        default=False, description="Whether the user has administrative privileges"
    )


class ApiUserOut(ApiUserIn):
    id: UUID = Field(description="The unique identifier of the user")
