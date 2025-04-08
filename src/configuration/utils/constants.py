"""Constants used in the project."""

from enum import Enum, auto

import numpy as np

# Fix the seed
np.random.seed(0)

# Conversion factors
PIXEL_TO_CM_PEDESTRIAN: float = 30.0 / (2.0 * 405.97552)
PIXEL_TO_CM_BIKE: float = 142.0 / 204.0
MM_TO_CM: float = 0.1
INCH_TO_CM: float = 2.54
LB_TO_KG: float = 0.453592
CM_TO_M: float = 0.01

# Initial agents / measures
DISK_NUMBER: int = 5

DEFAULT_FLOOR_DAMPING: float = 2.0  # Damping coefficient for the floor
DEFAULT_ANGULAR_DAMPING: float = 5.0  # Damping coefficient for the angular velocity

# Material properties
YOUNG_MODULUS_IRON: float = 1.0e6
YOUNG_MODULUS_HUMAN: float = 1.0e6
YOUNG_MODULUS_WOOD: float = 1.0e6
YOUNG_MODULUS_STONE: float = 1.0e6
YOUNG_MODULUS_ASPHALT: float = 1.0e6

POISSON_RATIO_IRON: float = 0.3
POISSON_RATIO_HUMAN: float = 0.3
POISSON_RATIO_WOOD: float = 0.3
POISSON_RATIO_STONE: float = 0.3
POISSON_RATIO_ASPHALT: float = 0.3

GAMMA_NORMAL: float = 1.3 * 10**4  # Damping coefficient for normal contact
GAMMA_TANGENTIAL: float = 1.3 * 10**4  # Damping coefficient for tangential contact
KINETIC_FRICTION: float = 0.5  # Coefficient of kinetic friction

# Crowd class
MAX_NB_ITERATIONS: int = 100  # Maximum number of iterations for the parking algorithm
DEFAULT_REPULSION_LENGTH: float = 15.0  # cm
DEFAULT_DESIRED_DIRECTION: float = 0.0  # degrees
DEFAULT_RANDOM_PACKING: bool = False
INFINITE: float = 1.0e10  # Infinite value for the simulation

# Crowd Statistics
DEFAULT_PEDESTRIAN_HEIGHT: float = 170.0  # cm
DEFAULT_BIKE_WEIGHT: float = 30.0  # kg
DEFAULT_PEDESTRIAN_WEIGHT: float = 70.0  # kg

# Decisional force and torque
DECISIONAL_TRANSLATIONAL_FORCE_X: float = 0.0  # N
DECISIONAL_TRANSLATIONAL_FORCE_Y: float = 0.0  # N
DECISIONAL_TORQUE: float = 0.0  # N.m

# Initial velocity
INITIAL_TRANSLATIONAL_VELOCITY_X: float = 0.0  # m/s
INITIAL_TRANSLATIONAL_VELOCITY_Y: float = 0.0  # m/s
INITIAL_ROTATIONAL_VELOCITY: float = 0.0  # rad/s


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


class CommonMeasures(Enum):
    """CommonMeasures is an enumeration that defines different common measures."""

    weight = auto()
    moment_of_inertia = auto()


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

    pedestrian_weight_min = auto()
    pedestrian_weight_max = auto()
    pedestrian_weight_mean = auto()
    pedestrian_weight_std_dev = auto()

    bike_weight_min = auto()
    bike_weight_max = auto()
    bike_weight_mean = auto()
    bike_weight_std_dev = auto()

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


class MaterialNames(Enum):
    """Enum for material names."""

    asphalt = auto()
    stone = auto()
    iron = auto()
    wood = auto()
    human = auto()


class MaterialProperties(Enum):
    """Enum for material properties."""

    young_modulus = auto()
    poisson_ratio = auto()


class MaterialsContactProperties(Enum):
    """Enum for the properties of the contact between two materials."""

    gamma_normal = auto()
    gamma_tangential = auto()
    kinetic_friction = auto()
