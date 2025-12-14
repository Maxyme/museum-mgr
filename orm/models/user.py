from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from api_models.base import Base


class User(Base):
    __tablename__ = "user"
    name: Mapped[str] = mapped_column(
        CheckConstraint("char_length(name) >= 1", name="check_user_name_non_empty"),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        CheckConstraint("char_length(email) >= 1", name="check_user_email_non_empty"),
        nullable=False,
    )
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)
