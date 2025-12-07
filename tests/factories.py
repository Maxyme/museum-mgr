from polyfactory.factories.pydantic_factory import ModelFactory
from api_models.museum import MuseumCreate

class MuseumCreateFactory(ModelFactory[MuseumCreate]):
    __model__ = MuseumCreate
