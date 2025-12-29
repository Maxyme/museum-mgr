from pydantic import BaseModel, ConfigDict


class APIBase(BaseModel):
    """Base for all API models."""

    model_config = ConfigDict(from_attributes=True)
