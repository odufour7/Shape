"""This module defines the InitialState class."""

from shapely.geometry import MultiPolygon, Point, Polygon

import src.utils.constants as cst
import src.utils.functions as fun
from src.utils.typing_custom import AgentType, SapeDataType, Sex, ShapeType

# python -m src.classes.initial_pedestrian


class InitialPedestrian:
    """Encapsulates the initial pedestrian state."""

    def __init__(self, sex: Sex) -> None:
        """Initializes the initial state with shape data and derived constants."""

        if sex not in ["male", "female"]:
            raise ValueError("The sex should be either 'male' or 'female'.")

        self._agent_type: AgentType = cst.AgentTypes.pedestrian.name
        self._shapes: SapeDataType = self._initialize_shapes()
        self._shapes3D: dict[int, Polygon] = fun.load_pickle(
            cst.PICKLE_DIR / f"{sex}_3dBody.pkl"
        )
        self._measures: dict[str, float] = {
            cst.PedestrianParts.sex.name: sex,
            cst.PedestrianParts.bideltoid_breadth.name: 2.0
            * self._shapes["disk4"]["center"][0]
            + 2.0 * self._shapes["disk4"]["radius"],
            cst.PedestrianParts.chest_depth.name: 2.0 * self._shapes["disk2"]["radius"],
            cst.PedestrianParts.height.name: abs(
                max(self._shapes3D.keys()) - min(self._shapes3D.keys())
            ),
        }

    def _initialize_shapes(
        self,
    ) -> dict[str, dict[str, ShapeType | float | tuple[float, float]]]:
        """Initializes the shape data for the pedestrian."""
        # Define disk parameters (center coordinates and radii)
        disks = [
            {"center": (-552.7920, 0.00000), "radius": 282.41232},
            {"center": (-242.5697, 71.73901), "radius": 388.36243},
            {"center": (0.0000, 86.11438), "radius": 405.97552},
            {"center": (242.5697, 71.73901), "radius": 388.36243},
            {"center": (552.7920, 0.00000), "radius": 282.41232},
        ]

        # Convert disk data into a structured dictionary
        return {
            f"disk{i}": {
                "shape_type": cst.ShapeTypes.circle.name,
                "young_modulus": cst.YOUNG_MODULUS_DISK_INIT,
                "center": (
                    disk["center"][0] * cst.PIXEL_TO_CM_PEDESTRIAN,
                    disk["center"][1] * cst.PIXEL_TO_CM_PEDESTRIAN,
                ),
                "radius": disk["radius"] * cst.PIXEL_TO_CM_PEDESTRIAN,
            }
            for i, disk in enumerate(disks)
        }

    @property
    def sex(self) -> Sex:
        """Returns the sex."""
        return self._measures[cst.PedestrianParts.sex.name]

    @sex.setter
    def sex(self, value) -> None:
        """Set a new value for the sex."""
        if isinstance(value, str) and value not in ["male", "female"]:
            raise ValueError("The sex should be either 'male' or 'female'.")
        self._measures[cst.PedestrianParts.sex.name] = value
        self._body3D = fun.load_pickle(cst.PICKLE_DIR / f"{value}_3dBody.pkl")

    @property
    def agent_type(self) -> AgentType:
        """Returns the agent type."""
        return self._agent_type

    @property
    def shapes(self) -> SapeDataType:
        """Returns the shapes of the pedestrian."""
        return self._shapes

    @property
    def measures(self) -> dict[str, float]:
        """Returns the measures of the pedestrian."""
        return self._measures

    @property
    def shapes3D(self) -> dict[int, MultiPolygon]:
        """Returns the 3D body of the pedestrian."""
        return self._shapes3D

    def calculate_position(self):
        """Calculate the position of the pedestrian."""
        return Point(
            self.shapes["disk2"]["center"][0], self.shapes["disk2"]["center"][0]
        )

    def get_disk_centers(self):
        """Get the centers of the disks."""
        return [
            Point(self.shapes[f"disk{i}"]["center"]) for i in range(cst.DISK_NUMBER)
        ]

    def get_disk_radii(self):
        """Get the radii of the disks."""
        return [self.shapes[f"disk{i}"]["radius"] for i in range(cst.DISK_NUMBER)]


class InitialBike:
    """Encapsulates the initial bike state."""

    def __init__(self) -> None:
        """Initializes the initial state with shape data and derived constants."""
        self._agent_type: AgentType = cst.AgentTypes.bike.name
        self._shapes: SapeDataType = self._initialize_shapes()
        self._measures: dict[str, float] = {
            cst.BikeParts.wheel_width.name: self._shapes["bike"]["max_x"]
            - self._shapes["bike"]["min_x"],
            cst.BikeParts.total_length.name: self._shapes["bike"]["max_y"]
            - self._shapes["bike"]["min_y"],
            cst.BikeParts.handlebar_length.name: self._shapes["rider"]["max_x"]
            - self._shapes["rider"]["min_x"],
            cst.BikeParts.top_tube_length.name: self._shapes["rider"]["max_y"]
            - self._shapes["rider"]["min_y"],
        }

    def _initialize_shapes(
        self,
    ) -> dict[str, dict[str, ShapeType | float | tuple[float, float]]]:
        """Initializes the shape data for the bike.
        There is two composite shapes: the bike and the rider.
        """
        # define the bike as a rectangle
        rider = {
            "min_x": 62.0,
            "min_y": 96.0,
            "max_x": 62.0 + 86.0,
            "max_y": 96.0 + 99.0,
        }
        # define the rider as a rectangle orthogonal to the bike
        bike = {
            "min_x": 96.0,
            "min_y": 46.0,
            "max_x": 96.0 + 16.0,
            "max_y": 46.0 + 204.0,
        }
        # put the CM to (0,0) and convert to cm
        center_of_mass_bike = Point(
            (bike["min_x"] + bike["max_x"]) / 2.0, (bike["min_y"] + bike["max_y"]) / 2.0
        )
        center_of_mass_rider = Point(
            (rider["min_x"] + rider["max_x"]) / 2.0,
            (rider["min_y"] + rider["max_y"]) / 2.0,
        )
        bike["min_x"] = bike["min_x"] - center_of_mass_bike.x
        bike["min_y"] = bike["min_y"] - center_of_mass_bike.y
        bike["max_x"] = bike["max_x"] - center_of_mass_bike.x
        bike["max_y"] = bike["max_y"] - center_of_mass_bike.y
        rider["min_x"] = rider["min_x"] - center_of_mass_rider.x
        rider["min_y"] = rider["min_y"] - center_of_mass_rider.y
        rider["max_x"] = rider["max_x"] - center_of_mass_rider.x
        rider["max_y"] = rider["max_y"] - center_of_mass_rider.y

        for key in bike:
            bike[key] = bike[key] * cst.PIXEL_TO_CM_BIKE
        for key in rider:
            rider[key] = rider[key] * cst.PIXEL_TO_CM_BIKE

        return {
            "bike": {
                "shape_type": cst.ShapeTypes.rectangle.name,
                "young_modulus": cst.YOUNG_MODULUS_RECTANGLE_INIT,
                "min_x": bike["min_x"],
                "min_y": bike["min_y"],
                "max_x": bike["max_x"],
                "max_y": bike["max_y"],
            },
            "rider": {
                "shape_type": cst.ShapeTypes.rectangle.name,
                "young_modulus": cst.YOUNG_MODULUS_RECTANGLE_INIT,
                "min_x": rider["min_x"],
                "min_y": rider["min_y"],
                "max_x": rider["max_x"],
                "max_y": rider["max_y"],
            },
        }

    @property
    def agent_type(self) -> AgentType:
        """Returns the agent type."""
        return self._agent_type

    @property
    def shapes(self) -> SapeDataType:
        """Returns the shapes of the pedestrian."""
        return self._shapes

    @property
    def measures(self) -> dict[str, float]:
        """Returns the measures of the pedestrian."""
        return self._measures

    def calculate_position(self):
        """Calculate the position of the bike."""
        return Point(
            (self.shapes["bike"]["max_x"] + self.shapes["bike"]["min_x"]) / 2.0,
            (self.shapes["bike"]["max_y"] + self.shapes["bike"]["min_y"]) / 2.0,
        )
