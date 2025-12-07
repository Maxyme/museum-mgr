from advanced_alchemy.base import UUIDv7AuditBase
from sqlalchemy.orm import Mapped


class Museum(UUIDv7AuditBase):
    __tablename__ = "museum"
    city: Mapped[str]
    population: Mapped[int]
