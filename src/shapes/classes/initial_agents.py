"""Module defining the InitialState class."""

from pathlib import Path
from typing import Union

from shapely.geometry import MultiPolygon, Point

import shapes.utils.constants as cst
import shapes.utils.functions as fun
from shapes.utils.typing_custom import Sex, ShapeDataType, ShapeType


class InitialPedestrian:
    """
    Encapsulates the initial pedestrian state including its 2D shape data and derived measurements.

    Parameters
    ----------
    sex : Sex
            Biological sex of the pedestrian, must be either "male" or "female".
            This affects 3D body shape loading and biomechanical calculations.
    """

    def __init__(self, sex: Sex) -> None:
        """
        Initialize a pedestrian agent with biomechanical properties.

        Parameters
        ----------
        sex : Sex
            Biological sex of the pedestrian, must be either "male" or "female".
            This affects 3D body shape loading and biomechanical calculations.

        Attributes
        ----------
        _agent_type : AgentTypes
            Agent type set to pedestrian (enum value)
        _shapes2D : ShapeDataType
            2D shape data with disk components representing body parts
        _shapes3D : dict[float, MultiPolygon]
            3D body layers mapped to z-height coordinates (in centimeters)
        _measures : dict[str, float | Sex | None]
            Biomechanical measurements including:
            - sex: Biological sex (Literal["male","female"])
            - bideltoid_breadth: Shoulder width derived from disk4
            - chest_depth: Torso depth from disk2
            - height: Vertical span of 3D body
            - weight: Default weight from constants file
            - moment_of_inertia: Initially uncalculated (None)

        Raises
        ------
        ValueError
            If provided sex is not "male" or "female"
        TypeError
            If sex argument is not a string

        Notes
        -----
        - 3D shapes are loaded from sex-specific pickle files in data/pkl/
        - 2D disk coordinates are in centimeters
        - Height calculation uses maximum z-coordinate difference from 3D data
        - Default weight from DEFAULT_PEDESTRIAN_WEIGHT
        - the moment_of_inertia will computed later when the agent will be created
        """
        if isinstance(sex, str) and sex not in ["male", "female"]:
            raise ValueError("The sex should be either 'male' or 'female'.")

        self._agent_type: cst.AgentTypes = cst.AgentTypes.pedestrian
        self._shapes2D: ShapeDataType = self._initialize_shapes()
        dir_path = Path(__file__).parent.parent.parent.parent.absolute() / "data" / "pkl"
        self._shapes3D: dict[float, MultiPolygon] = fun.load_pickle(dir_path / f"{sex}_3dBody.pkl")
        self._measures: dict[str, float | Sex | None] = {
            cst.PedestrianParts.sex.name: sex,
            cst.PedestrianParts.bideltoid_breadth.name: 2.0 * self._shapes2D["disk4"]["center"][0]
            + 2.0 * self._shapes2D["disk4"]["radius"]
            if (isinstance(self._shapes2D["disk4"]["center"], tuple) and isinstance(self._shapes2D["disk4"]["radius"], float))
            else 0.0,
            cst.PedestrianParts.chest_depth.name: 2.0 * self._shapes2D["disk2"]["radius"]
            if isinstance(self._shapes2D["disk2"]["radius"], float)
            else 0.0,
            cst.PedestrianParts.height.name: abs(max(self._shapes3D.keys()) - min(self._shapes3D.keys())),
            cst.CommonMeasures.weight.name: cst.DEFAULT_PEDESTRIAN_WEIGHT,
            cst.CommonMeasures.moment_of_inertia.name: None,
        }

    def _initialize_shapes(self) -> dict[str, dict[str, ShapeType | float | tuple[float, float]]]:
        """
        Initialize shape data for pedestrian body components.

        Creates and configures five circular disks representing key body features:
        - Disk0: Left arm
        - Disk1: Left pectoral muscle
        - Disk2: Central belly
        - Disk3: Right pectoral muscle
        - Disk4: Right arm

        Returns
        -------
        dict[str, dict[str, ShapeType | float | tuple[float, float]]]
            Nested dictionary containing circular shape data with:
                - Outer keys: Component IDs (e.g., "disk0" to "disk4")
                - Inner dictionaries containing:
                    * shape_type: "circle" (str from ShapeTypes enum name)
                    * young_modulus: Initial stiffness value (float)
                    * center: (x, y) coordinates in centimeters (tuple[float, float])
                    * radius: Disk radius in centimeters (float)

        Notes
        -----
        - Initial coordinates are defined in image pixels before conversion
        - Defaults to (0.0, 0.0) center and 0.0 radius if invalid data types found
        - Disk positions correspond to anatomical features:
            - Disk2 represents central belly
            - Disks 1/3 represent left/right pectoral muscle
            - Disks 0/4 represent left/right arms
        """
        # Define disk parameters (center coordinates and radii)
        disks: list[dict[str, Union[tuple[float, float], float]]] = [
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
                    disk["center"][0] * cst.PIXEL_TO_CM_PEDESTRIAN if isinstance(disk["center"], tuple) else 0.0,
                    disk["center"][1] * cst.PIXEL_TO_CM_PEDESTRIAN if isinstance(disk["center"], tuple) else 0.0,
                ),
                "radius": disk["radius"] * cst.PIXEL_TO_CM_PEDESTRIAN if isinstance(disk["radius"], float) else 0.0,
            }
            for i, disk in enumerate(disks)
        }

    @property
    def sex(self) -> Sex:
        """
        Get the biological sex of the pedestrian.

        Returns
        -------
        Literal["male", "female"]
            The biological sex of the pedestrian as either "male" or "female".

        Raises
        ------
        TypeError
            If the stored value is not a string or is not one of the allowed values
        """
        sex_name = self._measures[cst.PedestrianParts.sex.name]
        if isinstance(sex_name, str) and sex_name in ["male", "female"]:
            return sex_name
        raise TypeError(f"Expected type 'str' with value 'male' or 'female', but got {type(sex_name).__name__}")

    @sex.setter
    def sex(self, value: Sex) -> None:
        """
        Set the biological sex of the pedestrian and update associated 3D body model.

        Parameters
        ----------
        value : Literal["male", "female"]
            The biological sex to set. Must be exactly "male" or "female" (case-sensitive).

        Raises
        ------
        ValueError
            If provided value is not "male" or "female"
        TypeError
            If non-string value is provided
        """
        if isinstance(value, str) and value not in ["male", "female"]:
            raise ValueError("The sex should be either 'male' or 'female'.")
        self._measures[cst.PedestrianParts.sex.name] = value
        dir_path = Path(__file__).parent.parent.parent.parent.absolute() / "data" / "pkl"
        self._body3D = fun.load_pickle(dir_path / f"{value}_3dBody.pkl")

    @property
    def agent_type(self) -> cst.AgentTypes:
        """
        Get the type classification of the agent.

        Returns
        -------
        AgentTypes
            Enum member representing the agent's type classification (either "pedestrian", "bike" or "custom").
        """
        return self._agent_type

    @property
    def shapes2D(self) -> ShapeDataType:
        """
        Get the 2D geometric representation of the pedestrian's body components.

        Returns
        -------
        ShapeDataType
            Dictionary containing circular disk representations of body parts with:
                - Keys: Format "disk{N}" where N ranges 0-4 (e.g., "disk0", "disk1")
                - Values: Dictionaries with properties:
                    * shape_type: "circle" (from ShapeTypes enum)
                    * young_modulus: Material stiffness value (float)
                    * center: (x, y) coordinates in centimeters (tuple[float, float])
                    * radius: Disk radius in centimeters (float)
        """
        return self._shapes2D

    @property
    def measures(self) -> dict[str, float | Sex | None]:
        """
        Get the measures of the pedestrian.

        Returns
        -------
        dict[str, float | Sex | None]
            A dictionary containing the pedestrian's measures. The keys are measure names (str),
            and the values are either floats, "Sex" Literal["male","female"] values, or None.
        """
        return self._measures

    @property
    def shapes3D(self) -> dict[float, MultiPolygon]:
        """
        Get the 3D body representation of the pedestrian.

        This property provides access to the 3D shapes of the pedestrian, stored as a dictionary
        where each key is a float representing a layer or pedestrian slice, and each value is a "MultiPolygon"
        object representing the corresponding 2D geometry.

        Returns
        -------
        dict[float, MultiPolygon]
            A dictionary where:
                - Keys are float representing the height of each pedestrian slice.
                - Values are "MultiPolygon" objects representing the 2D geometry of each layer or slice.
        """
        return self._shapes3D

    def calculate_position(self) -> Point:
        """
        Calculate the pedestrian's position based on the center of disk2.

        The position is determined by the center coordinates of the "disk2" shape
        stored in the shapes2D attribute. This method assumes disk2 represents
        the pedestrian's main body position.

        Returns
        -------
        Point
            Point object containing (x, y) coordinates in centimeters:
                - x: First element of disk2's center coordinates
                - y: Second element of disk2's center coordinates

        Raises
        ------
        TypeError
            If the disk2 center value is not stored as a tuple of numerical values
        """
        if isinstance(self.shapes2D["disk2"]["center"], tuple):
            return Point(self.shapes2D["disk2"]["center"][0], self.shapes2D["disk2"]["center"][0])
        raise TypeError(f"Expected type 'tuple' with two floats, but got {type(self.shapes2D['disk2']['center']).__name__}")

    def get_disk_centers(self) -> list[Point]:
        """
        Retrieve the center coordinates of all disks.

        This method iterates through the predefined number of disks (specified by "DISK_NUMBER")
        and extracts their center coordinates from the "shapes2D" attribute.

        Returns
        -------
        list[Point]
            A list of Point objects representing the center coordinates of each disk in centimeters.
            The points are returned in the order of disk indices (disk0, disk1, ..., diskN-1).

        Notes
        -----
        Requires disks to be named consecutively as 'disk0', 'disk1', ..., 'disk{DISK_NUMBER-1}'
        in the shapes2D attribute
        Each disk entry must contain a "center" key with coordinate data compatible with Point constructor
        Returns empty Points for any missing or invalid disk entries
        """
        return [Point(self.shapes2D[f"disk{i}"]["center"]) for i in range(cst.DISK_NUMBER)]

    def get_disk_radii(self) -> list[float]:
        """
        Retrieve the radii of all disks.

        This method accesses the 'shapes2D' attribute of the instance and extracts the radius
        of each disk based on a predefined number of disks specified by 'DISK_NUMBER'.

        Returns
        -------
        list[float]
            A list containing the radii of the disks. Each element is a float
            representing the radius of a disk in the order they are stored.

        Notes
        -----
        - The method assumes that disk shapes are named 'disk0', 'disk1', etc., up to
          'disk{DISK_NUMBER - 1}'.
        - Only valid float radii are included in the returned list. If a disk's radius
          is not a float, it will be skipped.
        - If no valid radii are found, an empty list is returned.
        """
        list_of_radii: list[float] = []
        for i in range(cst.DISK_NUMBER):
            radius = self.shapes2D[f"disk{i}"]["radius"]
            if isinstance(radius, float):
                list_of_radii.append(radius)
        return list_of_radii


class InitialBike:
    """Encapsulates the initial state of a bike, including its 2D shape data and derived measurements."""

    def __init__(self) -> None:
        """
        Initialize an instance of the InitialBike class.

        Attributes
        ----------
        _agent_type : AgentTypes
            The type of agent, initialized to 'bike'.
        _shapes2D : ShapeDataType
            The 2D shape data initialized by the "_initialize_shapes" method.
        _measures : dict[str, float | None]
            A dictionary containing measurements derived from the shape data.
            Keys are defined in BikeParts and CommonMeasures enums:
            - 'wheel_width': The width of the bike's wheel.
            - 'total_length': The total length of the bike.
            - 'handlebar_length': The length of the rider's handlebar.
            - 'top_tube_length': The length of the rider's top tube.
            - 'moment_of_inertia': The moment of inertia (initially set to None).

        Notes
        -----
        - All measurements are calculated in centimeters.
        - If shape data is invalid or missing, measurements default to 0.0.
        - The moment of inertia is initially set to None and should be calculated separately.
        """
        self._agent_type: cst.AgentTypes = cst.AgentTypes.bike
        self._shapes2D: ShapeDataType = self._initialize_shapes()
        self._measures: dict[str, float | None] = {
            cst.BikeParts.wheel_width.name: self._shapes2D["bike"]["max_x"] - self._shapes2D["bike"]["min_x"]
            if isinstance(self._shapes2D["bike"]["max_x"], float) and isinstance(self._shapes2D["bike"]["min_x"], float)
            else 0.0,
            cst.BikeParts.total_length.name: self._shapes2D["bike"]["max_y"] - self._shapes2D["bike"]["min_y"]
            if isinstance(self._shapes2D["bike"]["max_y"], float) and isinstance(self._shapes2D["bike"]["min_y"], float)
            else 0.0,
            cst.BikeParts.handlebar_length.name: self._shapes2D["rider"]["max_x"] - self._shapes2D["rider"]["min_x"]
            if isinstance(self._shapes2D["rider"]["max_x"], float) and isinstance(self._shapes2D["rider"]["min_x"], float)
            else 0.0,
            cst.BikeParts.top_tube_length.name: self._shapes2D["rider"]["max_y"] - self._shapes2D["rider"]["min_y"]
            if isinstance(self._shapes2D["rider"]["max_y"], float) and isinstance(self._shapes2D["rider"]["min_y"], float)
            else 0,
            cst.CommonMeasures.moment_of_inertia.name: None,
        }

    def _initialize_shapes(self) -> dict[str, dict[str, ShapeType | float]]:
        """
        Initialize 2D shape data for the bicycle and rider.

        Creates rectangular shapes for both bicycle and rider, then:
        1. Calculates their original center of mass
        2. Adjusts coordinates to set center of mass at (0,0)
        3. Converts coordinates from pixels to centimeters using PIXEL_TO_CM_BIKE

        Returns
        -------
        dict[str, dict[str, ShapeType | float]]
            Nested dictionary containing shape data with two keys:
            - "bike": Dictionary of bicycle shape properties
            - "rider": Dictionary of rider shape properties

            Each shape dictionary contains:
            - shape_type: ShapeTypes.rectangle.name (str)
            - young_modulus: Initial Young's modulus value (float)
            - min_x: Minimum x-coordinate in cm (float)
            - min_y: Minimum y-coordinate in cm (float)
            - max_x: Maximum x-coordinate in cm (float)
            - max_y: Maximum y-coordinate in cm (float)
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
    def agent_type(self) -> cst.AgentTypes:
        """
        Get the type of the agent.

        Returns
        -------
        AgentTypes
            Enum member representing the agent's type classification (either "pedestrian", "bike" or "custom").
        """
        return self._agent_type

    @property
    def shapes2D(self) -> ShapeDataType:
        """
        Get the 2D shapes associated with the pedestrian.

        Returns
        -------
        ShapeDataType
            An object containing the 2D shapes associated with the pedestrian.
        """
        return self._shapes2D

    @property
    def measures(self) -> dict[str, float | None]:
        """
        Get the measures of the pedestrian.

        This property provides access to the measures of the pedestrian,
        which are stored in a dictionary. The keys are strings representing
        the names of the measures, and the values are floats or None
        representing the measure values.

        Returns
        -------
        dict[str, float | None]
            A dictionary containing the measures of the pedestrian.
            Keys are measure names (str) and values are measure values (float or None).
        """
        return self._measures

    def calculate_position(self) -> Point:
        """
        Calculate the central position of the bike.

        This method computes the central position of the bike based on the
        minimum and maximum x and y coordinates of the bike's shape.

        Returns
        -------
        Point
            A Point object representing the central position of the bike.

        Notes
        -----
            If the required shape coordinates are not available or not of the correct type,
            the method returns a Point(0.0, 0.0).
        """
        if (
            isinstance(self.shapes2D["bike"]["min_x"], float)
            and isinstance(self.shapes2D["bike"]["max_x"], float)
            and isinstance(self.shapes2D["bike"]["min_y"], float)
            and isinstance(self.shapes2D["bike"]["max_y"], float)
        ):
            return Point(
                (self.shapes2D["bike"]["max_x"] + self.shapes2D["bike"]["min_x"]) / 2.0,
                (self.shapes2D["bike"]["max_y"] + self.shapes2D["bike"]["min_y"]) / 2.0,
            )
        return Point(0.0, 0.0)
