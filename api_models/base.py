from advanced_alchemy.base import UUIDv7AuditBase

class Base(UUIDv7AuditBase):
    """Shared base for all models to ensure shared metadata/registry."""
    __abstract__ = True
