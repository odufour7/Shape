"""Constants used in the project."""

from enum import Enum, auto
from types import MappingProxyType

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
M_TO_CM: float = 100.0

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

SHEAR_MODULUS_IRON: float = 1.0e6
SHEAR_MODULUS_HUMAN: float = 1.0e6
SHEAR_MODULUS_WOOD: float = 1.0e6
SHEAR_MODULUS_STONE: float = 1.0e6
SHEAR_MODULUS_ASPHALT: float = 1.0e6

GAMMA_NORMAL: float = 1.3 * 10**4  # Damping coefficient for normal contact
GAMMA_TANGENTIAL: float = 1.3 * 10**4  # Damping coefficient for tangential contact
KINETIC_FRICTION: float = 0.5  # Coefficient of kinetic friction

# Crowd class
DEFAULT_AGENT_NUMBER: int = 4
MAX_NB_ITERATIONS: int = 80  # Maximum number of iterations for the parking algorithm
DEFAULT_REPULSION_LENGTH: float = 15.0  # cm
DEFAULT_DESIRED_DIRECTION: float = 0.0  # degrees
DEFAULT_RANDOM_PACKING: bool = False
INFINITE: float = 1.0e10  # Infinite value for the simulation

# Crowd Statistics
DEFAULT_PEDESTRIAN_HEIGHT: float = 170.0  # cm
DEFAULT_BIKE_WEIGHT: float = 30.0  # kg
DEFAULT_PEDESTRIAN_WEIGHT: float = 70.0  # kg

# Decisional force and torque
DECISIONAL_TRANSLATIONAL_FORCE_X: float = 10.0**3  # N
DECISIONAL_TRANSLATIONAL_FORCE_Y: float = 10.0**3  # N
DECISIONAL_TORQUE: float = 0.0  # N.m

# Initial velocity
INITIAL_TRANSLATIONAL_VELOCITY_X: float = 0.0  # m/s
INITIAL_TRANSLATIONAL_VELOCITY_Y: float = 0.0  # m/s
INITIAL_ROTATIONAL_VELOCITY: float = 0.0  # rad/s

# Agent Interactions
INITIAL_TANGENTIAL_FORCE_X: float = 0.0  # N
INITIAL_TANGENTIAL_FORCE_Y: float = 0.0  # N
INITIAL_NORMAL_FORCE_X: float = 0.0  # N
INITIAL_NORMAL_FORCE_Y: float = 0.0  # N
INITIAL_TANGENTIAL_RELATIVE_DISPLACEMENT_NORM: float = 0.0  # m


class BackupDataTypes(Enum):
    """Enum for backup data types."""

    zip = auto()
    pickle = auto()
    xml = auto()


class AgentTypes(Enum):
    """Enum for agent types."""

    pedestrian = auto()
    bike = auto()
    custom = auto()


class ShapeTypes(Enum):
    """Enum for shape types."""

    disk = auto()
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


CrowdStat = MappingProxyType(
    {
        "male_proportion": 0.5,
        "pedestrian_proportion": 1.0,
        "bike_proportion": 0.0,
        # Pedestrian weights (in kg)
        "pedestrian_weight_min": 10.0,  # kg
        "pedestrian_weight_max": 100.0,  # kg
        "pedestrian_weight_mean": 70.0,  # kg
        "pedestrian_weight_std_dev": 5.0,  # kg
        # Bike weights (in kg)
        "bike_weight_min": 10.0,  # kg
        "bike_weight_max": 100.0,  # kg
        "bike_weight_mean": 30.0,  # kg
        "bike_weight_std_dev": 5.0,  # kg
        # Male measurements (in cm)
        "male_bideltoid_breadth_min": 30.0,  # cm
        "male_bideltoid_breadth_max": 90.0,  # cm
        "male_bideltoid_breadth_mean": 51.0,  # cm
        "male_bideltoid_breadth_std_dev": 2.0,  # cm
        "male_chest_depth_min": 15.0,  # cm
        "male_chest_depth_max": 50.0,  # cm
        "male_chest_depth_mean": 26.0,  # cm
        "male_chest_depth_std_dev": 2.0,  # cm
        # Female measurements (in cm)
        "female_bideltoid_breadth_min": 30.0,  # cm
        "female_bideltoid_breadth_max": 90.0,  # cm
        "female_bideltoid_breadth_mean": 45.0,  # cm
        "female_bideltoid_breadth_std_dev": 1.5,  # cm
        "female_chest_depth_min": 15.0,  # cm
        "female_chest_depth_max": 50.0,  # cm
        "female_chest_depth_mean": 24.0,  # cm
        "female_chest_depth_std_dev": 1.5,  # cm
        # Wheel dimensions (in cm)
        "wheel_width_min": 5.0,  # cm
        "wheel_width_max": 30.0,  # cm
        "wheel_width_mean": 10.0,  # cm
        "wheel_width_std_dev": 2.0,  # cm
        # Total length (in cm)
        "total_length_min": 100.0,  # cm
        "total_length_max": 200.0,  # cm
        "total_length_mean": 142.0,  # cm
        "total_length_std_dev": 5.0,  # cm
        # Handlebar dimensions (in cm)
        "handlebar_length_min": 30.0,  # cm
        "handlebar_length_max": 90.0,  # cm
        "handlebar_length_mean": 45.0,  # cm
        "handlebar_length_std_dev": 5.0,  # cm
        # Top tube dimensions (in cm)
        "top_tube_length_min": 40.0,  # cm
        "top_tube_length_max": 90.0,  # cm
        "top_tube_length_mean": 61.0,  # cm
        "top_tube_length_std_dev": 5.0,  # cm
    }
)


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
    shear_modulus = auto()


class MaterialsContactProperties(Enum):
    """Enum for the properties of the contact between two materials."""

    gamma_normal = auto()
    gamma_tangential = auto()
    kinetic_friction = auto()
