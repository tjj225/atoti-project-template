from __future__ import annotations

from types import TracebackType

import atoti as tt

from .config import Config
from .load_tables import load_tables
from .start_session import set_password, start_session
from .util import run_periodically


class App:
    """Regroup the session with other resources so that they can be closed together."""

    def __init__(self, *, config: Config) -> None:
        # The config is kept private to deter passing an App to functions when a Config is all they need.
        self._session = start_session(config=config)
        self._stop_refreshing_data = (
            run_periodically(
                lambda: load_tables(self.session, config=config),
                period=config.data_refresh_period,
            )
            if config.data_refresh_period
            else None
        )

        self._stop_rotating_pass = (
            run_periodically(
                lambda: set_password(self.session, config=config),
                period=config.password_refresh_period,
            )
            if config.password_refresh_period
            else None
        )

    @property
    def session(self) -> tt.Session:
        return self._session

    def close(self) -> None:
        if self._stop_refreshing_data:
            self._stop_refreshing_data()
        if self._stop_rotating_pass:
            self._stop_rotating_pass()
        self.session.close()

    def __enter__(self) -> App:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
