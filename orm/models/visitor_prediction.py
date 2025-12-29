from uuid import UUID
from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from orm.models.base import Base
from orm.models.city import City


class VisitorPrediction(Base):
    __tablename__ = "visitor_prediction"

    city_id: Mapped[UUID] = mapped_column(ForeignKey("city.id"), nullable=False)
    predicted_visitors: Mapped[int] = mapped_column(
        CheckConstraint(
            "predicted_visitors >= 0", name="check_predicted_visitors_non_negative"
        ),
        nullable=False,
    )

    city: Mapped[City] = relationship()
