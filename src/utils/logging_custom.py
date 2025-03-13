"""Logging setup for the project."""

import logging


def setup_logging() -> None:
    """Set up logging configuration for the application.

    Configures the logging system with the following settings:
    - Log level: INFO
    - Log format: "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    - Date format: "%Y-%m-%d %H:%M:%S"

    This ensures that log messages include the timestamp, log level, filename, line number,
    and the message content for better debugging and monitoring.

    Returns
    -------
    None
        This function does not return a value.

    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
