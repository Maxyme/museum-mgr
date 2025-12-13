from pydantic import PostgresDsn, computed_field, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    MUSEUM_DB_NAME: str
    BROKER_DB_NAME: str
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    db_type: str = Field(default="postgresql", description="Database type")
    driver: str = Field(default="asyncpg", description="Database drive")

    @computed_field
    @property
    def db_url(self) -> str:
        """Get db url. Note the protocol needs the driver."""
        return f"{self.db_type}+{self.driver}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.MUSEUM_DB_NAME}"

    @computed_field
    @property
    def broker_url(self) -> str:
        """Get the broker url. Note the protocol doesn't need to be included for PGQueuer."""
        return f"{self.db_type}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.BROKER_DB_NAME}"

settings = Settings()
