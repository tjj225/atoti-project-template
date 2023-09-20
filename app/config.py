# ruff: noqa: UP007
# Pydantic evaluates type annotations at runtime which does not support `|`.

from __future__ import annotations

from collections.abc import Sequence
from datetime import timedelta
from pathlib import Path
from typing import Annotated, Optional, Union

from pydantic import (
    AliasChoices,
    DirectoryPath,
    Field,
    FilePath,
    HttpUrl,
    PostgresDsn,
    TypeAdapter,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from .util import normalize_postgres_dsn_for_atoti_sql


class Config(BaseSettings):
    """Hold all the configuration properties of the app, not only the ones related to Atoti.

    See https://pydantic-docs.helpmanual.io/usage/settings/.
    """

    model_config = SettingsConfigDict(frozen=True)

    data_refresh_period: Optional[timedelta] = timedelta(minutes=1)
    password_refresh_period: Optional[timedelta] = timedelta(seconds=10)

    # The $PORT environment variable is used by most PaaS to indicate the port the app server should bind to.
    port: int = 9090

    requests_timeout: timedelta = timedelta(seconds=30)

    java_options: Optional[Sequence[str]] = [
        "-Xms10g",
        "-Xmx10g",
        "-Dmanagement.endpoint.shutdown.enabled=true",
    ]
    log_file: str = "./server_template.log"

    _ROOT_DIRECTORY = Path(__file__).parent.parent
    _TESTS_DATA_PATH = _ROOT_DIRECTORY / "tests/data"

    reverse_geocoding_path: Union[HttpUrl, FilePath] = TypeAdapter(
        FilePath
    ).validate_python(_TESTS_DATA_PATH / "station_location.csv")

    user_content_storage: Annotated[
        Optional[Union[PostgresDsn, Path]],
        Field(
            # $DATABASE_URL is used by some PaaS such to designate the URL of the app's primary database.
            # For instance: https://devcenter.heroku.com/articles/heroku-postgresql#designating-a-primary-database.
            validation_alias=AliasChoices("user_content_storage", "database_url")
        ),
    ] = Path("content")

    velib_data_base_path: Union[HttpUrl, DirectoryPath] = TypeAdapter(
        DirectoryPath
    ).validate_python(_TESTS_DATA_PATH)

    @field_validator("user_content_storage")
    @classmethod
    def normalize_postgres_dsn(cls, value: object) -> object:
        try:
            postgres_dsn: PostgresDsn = TypeAdapter(PostgresDsn).validate_python(value)
            return normalize_postgres_dsn_for_atoti_sql(postgres_dsn)
        except ValueError:
            return value
