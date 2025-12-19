from dataclasses import dataclass, field


@dataclass
class MuseumData:
    museum: str
    visitors_per_year: int


@dataclass
class CityData:
    name: str
    population: int
    visitors: int
    museums: list[MuseumData] = field(default_factory=list)
