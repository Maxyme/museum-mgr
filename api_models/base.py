from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


NonEmptyString = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]

class APIBase(BaseModel):
    """Base for all API models."""

    model_config = ConfigDict(from_attributes=True)
