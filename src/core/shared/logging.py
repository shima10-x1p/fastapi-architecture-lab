"""Logging configuration helpers.

Usage pattern
-------------
At application startup (e.g. FastAPI lifespan):

    from core.shared.logging import configure_logging
    from core.shared.settings import get_settings

    configure_logging(get_settings())

Inside any module:

    from core.shared.logging import get_logger

    logger = get_logger(__name__)
    logger.info("something happened")
"""

import logging

from core.shared.settings import Settings


def configure_logging(settings: Settings) -> None:
    """Configure the root logger using values from Settings.

    This should be called exactly once at application startup. Subsequent
    calls reconfigure the root logger in place (useful in tests).

    The log level is resolved via logging.getLevelName so both string names
    ("INFO") and numeric values work. An unrecognised level string falls back
    to INFO to avoid silently swallowing all output.
    """
    level = logging.getLevelName(settings.log_level.upper())
    if not isinstance(level, int):
        # getLevelName returns a string like "Level 99" for unknown names
        level = logging.INFO

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Replace all existing handlers so repeated calls in tests are idempotent
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(settings.log_format))
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger.

    Pass __name__ from the calling module to get a logger scoped to that
    module. The returned logger inherits its effective level from the root
    logger configured by configure_logging().
    """
    return logging.getLogger(name)
