"""Logging setup for the project."""

import logging


def setup_logging() -> None:
    """
    Configures the logging settings for the application.

    This function sets up the logging configuration with the following settings:
    - Log level: INFO
    - Log format: "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    - Date format: "%Y-%m-%d %H:%M:%S"

    This ensures that all log messages will include the timestamp, log level, filename,
    line number, and the log message itself.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
