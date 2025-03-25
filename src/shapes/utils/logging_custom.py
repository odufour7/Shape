"""Logging setup for the project."""

import logging


def setup_logging() -> None:
    """
    Set up logging configuration for the application.

    This function configures the logging system with predefined settings to ensure
    consistent and detailed log messages throughout the application.

    The logging configuration includes the following settings:

    - Log level: INFO (captures informational messages and above)
    - Log format: "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
      This format includes:
      - Timestamp (asctime)
      - Log level (levelname)
      - Filename (filename)
      - Line number (lineno)
      - Log message (message)
    - Date format: "%Y-%m-%d %H:%M:%S"
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.getLogger("dicttoxml").setLevel(logging.WARNING)
