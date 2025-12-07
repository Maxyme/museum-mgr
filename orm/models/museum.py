class Museum(UUIDAuditBase):
    __tablename__ = "museum"
    city: Mapped[str]
    population: Mapped[int]
