from uuid import UUID
from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from orm.models.base import UserAuditBase
from orm.models.city import City


class Museum(UserAuditBase):
    __tablename__ = "museum"

    city_id: Mapped[UUID] = mapped_column(ForeignKey("city.id"), nullable=False)
    population: Mapped[int] = mapped_column(
        CheckConstraint("population >= 0", name="check_museum_population_non_negative"),
        nullable=False,
    )

    city: Mapped[City] = relationship()
