"""Constants used in the project."""

from configuration.utils.typing_custom import Sex

# User Interface
FIRST_TAB_NAME: str = "One agent"
SECOND_TAB_NAME: str = "Crowd"
THIRD_TAB_NAME: str = "Anthropometry"
FOURTH_TAB_NAME: str = "About"

# 2D / 3D shapes tab
DEFAULT_PEDESTRIAN_HEIGHT: float = 170.0  # cm
DEFAULT_HEIGHT_MIN: float = 100.0  # in cm
DEFAULT_HEIGHT_MAX: float = 230.0  # in cm

MAX_TRANSLATION_X: float = 200.0  # cm
MAX_TRANSLATION_Y: float = 200.0  # cm

DEFAULT_SEX: Sex = "male"

# Crowd tab
DEFAULT_BOUNDARY_X: float = 200.0  # cm
DEFAULT_BOUNDARY_X_MIN: float = 50.0  # cm
DEFAULT_BOUNDARY_X_MAX: float = 2000.0  # cm
DEFAULT_BOUNDARY_Y: float = 200.0  # cm
DEFAULT_BOUNDARY_Y_MIN: float = 50.0  # cm
DEFAULT_BOUNDARY_Y_MAX: float = 2000.0  # cm

DEFAULT_AGENT_NUMBER: int = 4
DEFAULT_AGENT_NUMBER_MIN: int = 1
DEFAULT_AGENT_NUMBER_MAX: int = 300

MAX_MOVE_X: float = 50.0  # cm
MAX_MOVE_Y: float = 50.0  # cm
MAX_ROTATION_ANGLE: float = 30.0  # degrees

DEFAULT_REPULSION_LENGTH_MIN: float = 1.0
DEFAULT_REPULSION_LENGTH_MAX: float = 70.0

DEFAULT_WALL_INTERACTION: float = False

# Developer
SHOW_DEV: bool = False
