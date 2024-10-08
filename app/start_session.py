from __future__ import annotations

import sys
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

    return tt.Session.start(
        tt.SessionConfig(
            logging=tt.LoggingConfig(destination=sys.stdout),
            port=config.port,
            user_content_storage=user_content_storage,
            java_options=[
                "-Dspring.profiles.active=application-monitoring",
                "-Djson.log.dir=/tmp",
                "-Dotel.java.global-autoconfigure.enabled=true",
                "-Dotel.logs.exporter=otlp",
                "-Dotel.metrics.exporter=otlp",
                "-Dotel.traces.exporter=otlp",
                "-Dotel.exporter.otlp.endpoint=http://localhost:4317",
                "-Dotel.traces.sampler=always_on",
                "-Dotel.metric.export.interval=60000",
                "-Dotel.resource.attributes=service.name=dev1-basline-atoti,service.version=1.0",
            ],
        ),
    )


def start_session(*, config: Config) -> tt.Session:
    """Start the session, declare the data model and load the initial data."""
    session = create_session(config=config)
    create_and_join_tables(session)
    create_cubes(session)
    # load_tables(session, config=config)
    return session
