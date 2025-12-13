from polyfactory.factories.pydantic_factory import ModelFactory
from api_models.museum import MuseumCreate
from api_models.user import UserCreate


class MuseumCreateFactory(ModelFactory[MuseumCreate]):
    __model__ = MuseumCreate


class UserCreateFactory(ModelFactory[UserCreate]):
    __model__ = UserCreate
