from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from orm.models.base import Base


class City(Base):
    __tablename__ = "city"
    name: Mapped[str] = mapped_column(
        CheckConstraint("char_length(name) >= 1", name="check_city_name_non_empty"),
        unique=True,
        nullable=False,
    )
    population: Mapped[int] = mapped_column(
        CheckConstraint("population >= 0", name="check_city_population_non_negative"),
        nullable=False,
    )
