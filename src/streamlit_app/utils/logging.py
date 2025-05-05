"""Logging setup for the project."""

import logging


def setup_logging() -> None:
    """
    Set up logging configuration for the application.

    Examples
    --------
    >>> import logging
    >>> setup_logging()
    >>> logging.info("This is an informational message.")
    2025-05-05 13:42:00 - INFO - your_script.py:25 - This is an informational message.
    >>> logging.warning("This is a warning message.")
    2025-05-05 13:42:00 - WARNING - your_script.py:26 - This is a warning message.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.getLogger("dicttoxml").setLevel(logging.WARNING)
