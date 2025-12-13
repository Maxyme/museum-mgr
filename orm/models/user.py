from sqlalchemy.orm import Mapped, mapped_column
from api_models.base import Base


class User(Base):
    __tablename__ = "user"
    name: Mapped[str]
    email: Mapped[str]
    is_admin: Mapped[bool] = mapped_column(default=False)
