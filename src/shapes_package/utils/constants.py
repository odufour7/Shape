"""Constants used in the project."""

from enum import Enum, auto

import numpy as np

from src.shapes_package.utils.typing_custom import Sex

PIXEL_TO_CM_PEDESTRIAN: float = 30.0 / (2.0 * 405.97552)
PIXEL_TO_CM_BIKE: float = 142.0 / 204.0
MM_TO_CM: float = 0.1
INCH_TO_CM: float = 2.54

YOUNG_MODULUS_DISK_INIT: float = 1.0e6
YOUNG_MODULUS_RECTANGLE_INIT: float = 1.0e6

DEG_TO_RAD: float = np.pi / 180.0  # Conversion factor from degrees to radians
DISK_NUMBER: int = 5
# DATA_DIR: Path = Path("./data")
# PICKLE_DIR: Path = DATA_DIR / "pickle"
# CSV_DIR: Path = DATA_DIR / "csv"
# JSON_DIR: Path = DATA_DIR / "json"

FIRST_TAB_NAME: str = "About"
SECOND_TAB_NAME: str = "2D agent"
THIRD_TAB_NAME: str = "3D pedestrian"
FOURTH_TAB_NAME: str = "Anthropometry"
FIFTH_TAB_NAME: str = "Crowd"
SIXTH_TAB_NAME: str = "Custom crowd"

# 2D shapes tab
DEFAULT_CHEST_DEPTH: float = 25.0
DEFAULT_CHEST_DEPTH_MIN: float = 15.0  # in cm
DEFAULT_CHEST_DEPTH_MAX: float = 50.0  # in cm
DEFAULT_BIDELTOID_BREADTH: float = 45.0
DEFAULT_BIDELTOID_BREADTH_MIN: float = 30.0  # in cm
DEFAULT_BIDELTOID_BREADTH_MAX: float = 90.0  # in cm
DEFAULT_HEIGHT: float = 170.0
DEFAULT_HEIGHT_MIN: float = 100.0  # in cm
DEFAULT_HEIGHT_MAX: float = 230.0  # in cm
DEFAULT_SEX: Sex = "male"

DEFAULT_HANDLEBAR_LENGTH: float = 60.0  # cm
DEFAULT_TOP_TUBE_LENGTH: float = 61.0  # cm
DEFAULT_TOTAL_LENGTH: float = 142.0  # cm
DEFAULT_WHEEL_WIDTH: float = 16.0  # cm

MAX_TRANSLATION_X: float = 500.0  # cm
MAX_TRANSLATION_Y: float = 500.0  # cm

# Crowd tab
DEFAULT_BOUNDARY_X: float = 200.0  # cm
DEFAULT_BOUNDARY_X_MIN: float = 50.0  # cm
DEFAULT_BOUNDARY_X_MAX: float = 300.0  # cm
DEFAULT_BOUNDARY_Y: float = 200.0  # cm
DEFAULT_BOUNDARY_Y_MIN: float = 50.0  # cm
DEFAULT_BOUNDARY_Y_MAX: float = 300.0  # cm

DEFAULT_AGENT_NUMBER: int = 4
DEFAULT_AGENT_NUMBER_MIN: int = 1
DEFAULT_AGENT_NUMBER_MAX: int = 300
MAX_MOVE_X: float = 50.0  # cm
MAX_MOVE_Y: float = 50.0  # cm
MAX_ROTATION: float = 30.0  # degrees
MAX_NB_ITERATIONS: int = 100  # Maximum number of iterations for the parking algorithm

DEFAULT_DECAY_REPULSION_RATE: float = 1.0 / 15.0
DEFAULT_DECAY_REPULSION_RATE_MIN: float = 1.0 / 30.0
DEFAULT_DECAY_REPULSION_RATE_MAX: float = 1.0 / 5.0

# 2D Shapes tab / Custom crowd tab / Crowd tab (statistics)
DEFAULT_MALE_PROPORTION: float = 0.5
DEFAULT_PEDESTRIAN_PROPORTION: float = 1.0
DEFAULT_BIKE_PROPORTION: float = 1.0 - DEFAULT_PEDESTRIAN_PROPORTION


DEFAULT_MALE_CHEST_DEPTH_MEAN: float = 26.0
DEFAULT_MALE_CHEST_DEPTH_STD_DEV: float = 2.0
DEFAULT_MALE_BIDELTOID_BREADTH_MEAN: float = 51.0
DEFAULT_MALE_BIDELTOID_BREADTH_STD_DEV: float = 2.0

DEFAULT_FEMALE_CHEST_DEPTH_MEAN: float = 24.0
DEFAULT_FEMALE_CHEST_DEPTH_STD_DEV: float = 1.5
DEFAULT_FEMALE_BIDELTOID_BREADTH_MEAN: float = 45.0
DEFAULT_FEMALE_BIDELTOID_BREADTH_STD_DEV: float = 1.5

DEFAULT_WHEEL_WIDTH_MEAN: float = 16.0
DEFAULT_WHEEL_WIDTH_STD_DEV: float = 2.0
DEFAULT_WHEEL_WIDTH_MIN: float = 5.0  # cm
DEFAULT_WHEEL_WIDTH_MAX: float = 30.0  # cm
DEFAULT_TOTAL_LENGTH_MEAN: float = 142.0
DEFAULT_TOTAL_LENGTH_STD_DEV: float = 5.0
DEFAULT_TOTAL_LENGTH_MIN: float = 100.0  # cm
DEFAULT_TOTAL_LENGTH_MAX: float = 200.0  # cm
DEFAULT_HANDLEBAR_LENGTH_MEAN: float = 60.0
DEFAULT_HANDLEBAR_LENGTH_STD_DEV: float = 5.0
DEFAULT_HANDLEBAR_LENGTH_MIN: float = 30.0  # cm
DEFAULT_HANDLEBAR_LENGTH_MAX: float = 90.0  # cm
DEFAULT_TOP_TUBE_LENGTH_MEAN: float = 61.0
DEFAULT_TOP_TUBE_LENGTH_STD_DEV: float = 5.0
DEFAULT_TOP_TUBE_LENGTH_MIN: float = 40.0  # cm
DEFAULT_TOP_TUBE_LENGTH_MAX: float = 90.0  # cm


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
    """Enum for pedestrian parts."""

    sex = auto()
    bideltoid_breadth = auto()
    chest_depth = auto()
    height = auto()


class BikeParts(Enum):
    """Bike is an enumeration that defines different parts of a bike."""

    wheel_width = auto()
    total_length = auto()
    handlebar_length = auto()
    top_tube_length = auto()


class StatType(Enum):
    """StatType is an enumeration that defines different types of statistics."""

    mean = auto()
    std_dev = auto()
    min = auto()
    max = auto()


class CrowdStat(Enum):
    """Enum for crowd statistics."""

    male_proportion = auto()
    pedestrian_proportion = auto()
    bike_proportion = auto()

    male_bideltoid_breadth_mean = auto()
    male_bideltoid_breadth_std_dev = auto()
    male_bideltoid_breadth_min = auto()
    male_bideltoid_breadth_max = auto()
    male_chest_depth_mean = auto()
    male_chest_depth_std_dev = auto()
    male_chest_depth_min = auto()
    male_chest_depth_max = auto()

    female_bideltoid_breadth_mean = auto()
    female_bideltoid_breadth_std_dev = auto()
    female_bideltoid_breadth_min = auto()
    female_bideltoid_breadth_max = auto()
    female_chest_depth_mean = auto()
    female_chest_depth_std_dev = auto()
    female_chest_depth_min = auto()
    female_chest_depth_max = auto()

    wheel_width_mean = auto()
    wheel_width_std_dev = auto()
    wheel_width_min = auto()
    wheel_width_max = auto()
    total_length_mean = auto()
    total_length_std_dev = auto()
    total_length_min = auto()
    total_length_max = auto()
    handlebar_length_mean = auto()
    handlebar_length_std_dev = auto()
    handlebar_length_min = auto()
    handlebar_length_max = auto()
    top_tube_length_mean = auto()
    top_tube_length_std_dev = auto()
    top_tube_length_min = auto()
    top_tube_length_max = auto()
