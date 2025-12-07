from sqlalchemy.orm import Mapped

from api_models.base import Base


class User(Base):
    __tablename__ = "user"
    name: Mapped[str]
    email: Mapped[str]
