from __future__ import annotations

import sched
import sys
import time
from dataclasses import asdict
from pathlib import Path

import atoti as tt

from .config import Config
from .create_and_join_tables import create_and_join_tables
from .create_cubes import create_cubes
from .load_tables import load_tables


def create_session(*, config: Config) -> tt.Session:
    user_content_storage: Path | tt.UserContentStorageConfig | None = None

    if config.user_content_storage is not None:
        user_content_storage = (
            config.user_content_storage
            if isinstance(config.user_content_storage, Path)
            else tt.UserContentStorageConfig(url=str(config.user_content_storage))
        )
    loggingConfig = tt.LoggingConfig(destination=config.log_file)
    return tt.Session(
        authentication=tt.BasicAuthenticationConfig(realm="Atoti Realm"),
        logging=loggingConfig,
        port=config.port,
        user_content_storage=user_content_storage,
        java_options=config.java_options,
    )


def start_session(*, config: Config) -> tt.Session:
    """Start the session, declare the data model and load the initial data."""
    session = create_session(config=config)
    session.security.individual_roles["admin"] = ["ROLE_USER"]
    set_password(session, config=config)
    create_and_join_tables(session)
    create_cubes(session)
    load_tables(session, config=config)
    expose_endpoint(session, config=config)
    return session


def expose_endpoint(session: tt.Session, /, *, config: Config) -> None:
    @session.endpoint("roll", method="GET")
    def roll_dice(request, user, session):
        msg = "Roll a dice"
        print(msg)
        print(msg)
        print(msg)
        return msg

    @session.endpoint("whoami", method="GET")
    def whoami(request, user, session):
        return asdict(user)


def set_password(session: tt.Session, /, *, config: Config) -> None:
    password = "valutpass"
    print("setting password from vault")
    session.security.basic.credentials["admin"] = password
