"""This module defines the InitialState class."""

from pathlib import Path

from shapely.geometry import MultiPolygon, Point, Polygon

import src.utils.constants as cst
import src.utils.functions as fun
from src.utils.typing_custom import AgentType, SapeDataType, Sex, ShapeType


class InitialPedestrian:
    """Encapsulates the initial pedestrian state."""

    def __init__(self, sex: Sex) -> None:
        """
        Initializes an instance of the class with shape data and derived constants.

        Parameters:
            sex (Sex): The sex of the agent, should be either 'male' or 'female'.

        Raises:
            ValueError: If the provided sex is not 'male' or 'female'.

        Attributes:
            _agent_type (AgentType): The type of agent, initialized to pedestrian.
            _shapes (SapeDataType): The shape data initialized by the _initialize_shapes method.
            _shapes3D (dict[int, Polygon]): The 3D shape data loaded from a pickle file.
            _measures (dict[str, float]): A dictionary containing various measurements derived from the shape data.
        """

        if sex not in ["male", "female"]:
            raise ValueError("The sex should be either 'male' or 'female'.")

        self._agent_type: AgentType = cst.AgentTypes.pedestrian.name
        self._shapes: SapeDataType = self._initialize_shapes()
        dir_path = Path(__file__).parent.parent.parent.absolute() / "data" / "pkl"
        self._shapes3D: dict[int, Polygon] = fun.load_pickle(dir_path / f"{sex}_3dBody.pkl")
        self._measures: dict[str, float] = {
            cst.PedestrianParts.sex.name: sex,
            cst.PedestrianParts.bideltoid_breadth.name: 2.0 * self._shapes["disk4"]["center"][0]
            + 2.0 * self._shapes["disk4"]["radius"],
            cst.PedestrianParts.chest_depth.name: 2.0 * self._shapes["disk2"]["radius"],
            cst.PedestrianParts.height.name: abs(max(self._shapes3D.keys()) - min(self._shapes3D.keys())),
        }

    def _initialize_shapes(self) -> dict[str, dict[str, ShapeType | float | tuple[float, float]]]:
        """
        Initializes the shape data for the pedestrian.

        This method defines the parameters for a set of disks, including their
        center coordinates and radii, and converts this data into a structured
        dictionary format. Each disk is represented with its shape type, Young's
        modulus, center coordinates, and radius, all scaled by a constant factor.

        Returns:
            dict[str, dict[str, ShapeType | float | tuple[float, float]]]: A dictionary
            where each key is a disk identifier (e.g., "disk0") and each value is another
            dictionary containing the shape type, Young's modulus, center coordinates,
            and radius of the disk.
        """

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
        """
        Returns the sex of the pedestrian.

        Returns:
            Sex: The sex of the pedestrian.
        """

        return self._measures[cst.PedestrianParts.sex.name]

    @sex.setter
    def sex(self, value) -> None:
        """
        Set a new value for the sex of the agent.

        Args:
            value (str): The new sex value to be set. It should be either 'male' or 'female'.

        Raises:
            ValueError: If the provided value is not 'male' or 'female'.

        """

        if isinstance(value, str) and value not in ["male", "female"]:
            raise ValueError("The sex should be either 'male' or 'female'.")
        self._measures[cst.PedestrianParts.sex.name] = value
        dir_path = Path(__file__).parent.parent.parent.absolute() / "data" / "pkl"
        self._body3D = fun.load_pickle(dir_path / f"{value}_3dBody.pkl")

    @property
    def agent_type(self) -> AgentType:
        """
        Returns the type of the agent.

        Returns:
            AgentType: The type of the agent.
        """

        return self._agent_type

    @property
    def shapes(self) -> SapeDataType:
        """
        Returns the shapes of the pedestrian.

        Returns:
            SapeDataType: The shapes of the pedestrian.
        """

        return self._shapes

    @property
    def measures(self) -> dict[str, float]:
        """
        Returns the measures of the pedestrian.

        This property method provides access to the measures of the pedestrian,
        which are stored in a dictionary where the keys are strings representing
        the names of the measures and the values are floats representing the
        measurements.

        Returns:
            dict[str, float]: A dictionary containing the measures of the pedestrian.
        """

        return self._measures

    @property
    def shapes3D(self) -> dict[int, MultiPolygon]:
        """
        Returns the 3D body of the pedestrian.

        Returns:
            dict[int, MultiPolygon]: A dictionary where the keys are integers and the values are MultiPolygon objects representing the 3D shapes of the pedestrian.
        """

        return self._shapes3D

    def calculate_position(self):
        """
        Calculate the position of the pedestrian.

        Returns:
            Point: A Point object representing the position of the pedestrian,
                   based on the center coordinates of the "disk2" shape.
        """

        return Point(self.shapes["disk2"]["center"][0], self.shapes["disk2"]["center"][0])

    def get_disk_centers(self):
        """
        Retrieve the centers of all disks.

        This method iterates over the predefined number of disks and extracts their center points.

        Returns:
            list of Point: A list containing the center points of the disks.
        """

        return [Point(self.shapes[f"disk{i}"]["center"]) for i in range(cst.DISK_NUMBER)]

    def get_disk_radii(self):
        """
        Retrieve the radii of all disks.

        This method accesses the 'shapes' attribute of the instance and extracts the radius
        of each disk based on a predefined number of disks specified by 'cst.DISK_NUMBER'.

        Returns:
            list: A list containing the radii of the disks.
        """

        return [self.shapes[f"disk{i}"]["radius"] for i in range(cst.DISK_NUMBER)]


class InitialBike:
    """Encapsulates the initial bike state."""

    def __init__(self) -> None:
        """
        Initializes an instance of the class.

        This constructor sets up the initial state with shape data and derived constants.

        Attributes:
            _agent_type (AgentType): The type of agent, initialized to 'bike'.
            _shapes (SapeDataType): The shape data initialized by the `_initialize_shapes` method.
            _measures (dict[str, float]): A dictionary containing measurements derived from the shape data.
                - 'wheel_width': The width of the bike's wheel.
                - 'total_length': The total length of the bike.
                - 'handlebar_length': The length of the rider's handlebar.
                - 'top_tube_length': The length of the rider's top tube.
        """

        self._agent_type: AgentType = cst.AgentTypes.bike.name
        self._shapes: SapeDataType = self._initialize_shapes()
        self._measures: dict[str, float] = {
            cst.BikeParts.wheel_width.name: self._shapes["bike"]["max_x"] - self._shapes["bike"]["min_x"],
            cst.BikeParts.total_length.name: self._shapes["bike"]["max_y"] - self._shapes["bike"]["min_y"],
            cst.BikeParts.handlebar_length.name: self._shapes["rider"]["max_x"] - self._shapes["rider"]["min_x"],
            cst.BikeParts.top_tube_length.name: self._shapes["rider"]["max_y"] - self._shapes["rider"]["min_y"],
        }

    def _initialize_shapes(self) -> dict[str, dict[str, ShapeType | float | tuple[float, float]]]:
        """
        Initializes the shape data for the bike and the rider.

        This method defines two composite shapes: the bike and the rider, both as rectangles.
        It calculates their center of mass, adjusts their coordinates to set the center of mass to (0,0),
        and converts the coordinates from pixels to centimeters.

        Returns:
            dict[str, dict[str, ShapeType | float | tuple[float, float]]]: A dictionary containing the shape data for the bike and the rider.
                Each shape data includes:
                    - shape_type: The type of the shape (rectangle).
                    - young_modulus: The Young's modulus of the shape.
                    - min_x: The minimum x-coordinate of the shape.
                    - min_y: The minimum y-coordinate of the shape.
                    - max_x: The maximum x-coordinate of the shape.
                    - max_y: The maximum y-coordinate of the shape.
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
        center_of_mass_bike = Point((bike["min_x"] + bike["max_x"]) / 2.0, (bike["min_y"] + bike["max_y"]) / 2.0)
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
        """
        Returns the type of the agent.

        Returns:
            AgentType: The type of the agent.
        """

        return self._agent_type

    @property
    def shapes(self) -> SapeDataType:
        """
        Returns the shapes of the pedestrian.

        Returns:
            SapeDataType: The shapes associated with the pedestrian.
        """

        return self._shapes

    @property
    def measures(self) -> dict[str, float]:
        """
        Returns the measures of the pedestrian.

        This property method provides access to the measures of the pedestrian,
        which are stored in a dictionary where the keys are strings representing
        the names of the measures and the values are floats representing the
        measure values.

        Returns:
            dict[str, float]: A dictionary containing the measures of the pedestrian.
        """

        return self._measures

    def calculate_position(self):
        """
        Calculate the position of the bike.

        This method computes the central position of the bike based on the
        minimum and maximum x and y coordinates of the bike's shape.

        Returns:
            Point: A Point object representing the central position of the bike.
        """

        return Point(
            (self.shapes["bike"]["max_x"] + self.shapes["bike"]["min_x"]) / 2.0,
            (self.shapes["bike"]["max_y"] + self.shapes["bike"]["min_y"]) / 2.0,
        )
