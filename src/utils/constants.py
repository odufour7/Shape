"""Constants used in the project."""

from enum import Enum, auto
from pathlib import Path

import numpy as np

from src.utils.typing_custom import Sex

PIXEL_TO_CM_PEDESTRIAN: float = 30.0 / (2.0 * 405.97552)
PIXEL_TO_CM_BIKE: float = 142.0 / 204.0
MM_TO_CM: float = 0.1
INCH_TO_CM: float = 2.54

YOUNG_MODULUS_DISK_INIT: float = 1.0e6
YOUNG_MODULUS_RECTANGLE_INIT: float = 1.0e6

DEG_TO_RAD: float = np.pi / 180.0  # Conversion factor from degrees to radians
DISK_NUMBER: int = 5
DATA_DIR: Path = Path("./data")
PICKLE_DIR: Path = DATA_DIR / "pickle"
CSV_DIR: Path = DATA_DIR / "csv"

MIN_DENSITY: float = 1e-5  # in pedestrians per cm^2
MAX_DENSITY: float = 10.0  # in pedestrians per cm^2
MIN_CHEST_DEPTH: float = 15.0  # in cm
MAX_CHEST_DEPTH: float = 50.0  # in cm
MIN_BIDELTOID_BREADTH: float = 20.0  # in cm
MAX_BIDELTOID_BREADTH: float = 60.0  # in cm
MIN_HEIGHT: float = 100.0  # in cm
MAX_HEIGHT: float = 200.0  # in cm
MAX_NB_ITERATIONS: int = 100  # Maximum number of iterations for the parking algorithm

DEFAULT_CHEST_DEPTH: float = 25.0
DEFAULT_BIDELTOID_BREADTH: float = 45.0
DEFAULT_HEIGHT: float = 170.0
DEFAULT_SEX: Sex = "male"

DEFAULT_HANDLEBAR_LENGTH: float = 60.0  # cm
DEFAULT_TOP_TUBE_LENGTH: float = 61.0  # cm
DEFAULT_TOTAL_LENGTH: float = 142.0  # cm
DEFAULT_WHEEL_WIDTH: float = 16.0  # cm

MIN_HANDLEBAR_LENGTH: float = 30.0  # cm
MAX_HANDLEBAR_LENGTH: float = 90.0  # cm
MIN_TOP_TUBE_LENGTH: float = 40.0  # cm
MAX_TOP_TUBE_LENGTH: float = 90.0  # cm
MIN_TOTAL_LENGTH: float = 100.0  # cm
MAX_TOTAL_LENGTH: float = 200.0  # cm
MIN_WHEEL_WIDTH: float = 5.0  # cm
MAX_WHEEL_WIDTH: float = 30.0  # cm

FIRST_TAB_NAME: str = "About"
SECOND_TAB_NAME: str = "2D agent"
THIRD_TAB_NAME: str = "3D pedestrian"
FOURTH_TAB_NAME: str = "Anthropometry"
FIFTH_TAB_NAME: str = "Crowd"
SIXTH_TAB_NAME: str = "Custom crowd"

DEFAULT_DENSITY: float = 1e-3
DEDAULT_MEAN_CHEST_DEPTH: float = 22.0
DEDAULT_STD_CHEST_DEPTH: float = 3.0
DEDAULT_MEAN_BIDELTOID_BREADTH: float = 35.0
DEDAULT_STD_BIDELTOID_BREADTH: float = 3.0

DEFAULT_BOUNDARY_X: float = 100.0  # cm
DEFAULT_BOUNDARY_Y: float = 100.0  # cm


class BackupDataTypes(Enum):
    """Enum for backup data types."""

    json = auto()
    pickle = auto()
    xml = auto()


class AgentTypes(Enum):
    """Enum for agent types."""

    pedestrian = auto()
    bike = auto()
    custom = auto()


class ShapeTypes(Enum):
    """Enum for shape types."""

    circle = auto()
    rectangle = auto()
    polygon = auto()


class PedestrianParts(Enum):
    """Enum for pedestrian parts"""

    sex = auto()
    bideltoid_breadth = auto()
    chest_depth = auto()
    height = auto()


class BikeParts(Enum):
    """Enum for bike parts"""

    wheel_width = auto()
    total_length = auto()
    handlebar_length = auto()
    top_tube_length = auto()


class CrowdPedestrianStat(Enum):
    """Enum for a crowd made of pedestrians"""

    male_proportion = auto()

    mean_chest_depth = auto()
    std_dev_chest_depth = auto()
    min_chest_depth = auto()
    max_chest_depth = auto()

    mean_bideltoid_breadth = auto()
    std_dev_bideltoid_breadth = auto()
    min_bideltoid_breadth = auto()
    max_bideltoid_breadth = auto()


class CrowdBikeStat(Enum):
    """Enum for a crowd made of bikes"""

    number_of_bikes = auto()

    mean_handlebar_length = auto()
    std_dev_handlebar_length = auto()
    min_handlebar_length = auto()
    max_handlebar_length = auto()

    mean_top_tube_length = auto()
    std_dev_top_tube_length = auto()
    min_top_tube_length = auto()
    max_top_tube_length = auto()

    mean_total_length = auto()
    std_dev_total_length = auto()
    min_total_length = auto()
    max_total_length = auto()

    mean_wheel_width = auto()
    std_dev_wheel_width = auto()
    min_wheel_width = auto()
    max_wheel_width = auto()
