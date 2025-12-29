from polyfactory.factories.pydantic_factory import ModelFactory
from api_models.museum import MuseumCreate
from api_models.user import ApiUserIn


class MuseumCreateFactory(ModelFactory[MuseumCreate]):
    __model__ = MuseumCreate


class UserCreateFactory(ModelFactory[ApiUserIn]):
    __model__ = ApiUserIn
