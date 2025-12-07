from advanced_alchemy.base import UUIDv7AuditBase
from sqlalchemy.orm import Mapped

class User(UUIDv7AuditBase):
    __tablename__ = "user"
    name: Mapped[str]
    email: Mapped[str]
