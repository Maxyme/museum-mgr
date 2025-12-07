from sqlalchemy.orm import Mapped
from api_models.base import Base

class Museum(Base):
    __tablename__ = "museum"
    city: Mapped[str]
    population: Mapped[int]
