from uuid import UUID
from advanced_alchemy.base import UUIDv7AuditBase
from sqlalchemy.orm import Mapped, mapped_column


class Base(UUIDv7AuditBase):
    """Shared base for all models to ensure shared metadata/registry."""

    __abstract__ = True


class UserAuditBase(UUIDv7AuditBase):
    """Base for models that require user auditing."""

    __abstract__ = True

    user_id: Mapped[UUID] = mapped_column(nullable=False)
