""" Constants used in the project. """

from pathlib import Path

from src.utils.typing_custom import Sex

PIXEL_TO_CM: float = 30.0 / (2.0 * 405.97552)
DISK_NUMBER: int = 5
DATA_DIR: Path = Path("./data")
PICKLE_DIR: Path = DATA_DIR / "pickle"
CSV_DIR: Path = DATA_DIR / "csv"

MIN_DENSITY: float = 1e-5  # in pedestrians per cm^2
MAX_DENSITY: float = 10.0  # in pedestrians per cm^2
MIN_CHEST_DEPTH: float = 10.0  # in cm
MAX_CHEST_DEPTH: float = 50.0  # in cm
MIN_BIDELTOID_BREADTH: float = 10.0  # in cm
MAX_BIDELTOID_BREADTH: float = 60.0  # in cm
MIN_HEIGHT: float = 100.0  # in cm
MAX_HEIGHT: float = 200.0  # in cm
MAX_NB_ITERATIONS: int = 100  # Maximum number of iterations for the parking algorithm

DEFAULT_CHEST_DEPTH: float = 30.0
DEFAULT_BIDELTOID_BREADTH: float = 40.0
DEFAULT_HEIGHT: float = 180.0
DEFAULT_SEX: Sex = "male"
