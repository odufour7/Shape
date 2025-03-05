""" This module defines classes to store physical attributes and geometry of agents. """

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Literal, TypeAlias, Union, get_args

from shapely.affinity import rotate, scale, translate
from shapely.geometry import MultiPoint, Point, Polygon  # Ensure shapely is installed

# Type aliases
Sex: TypeAlias = Literal["male", "female"]
AgentType: TypeAlias = Literal["pedestrian", "bike", "custom"]
ShapeType: TypeAlias = Literal["circle", "rectangle", "ellipse", "polygon"]
SapeDataType: TypeAlias = (
    dict[str, dict[str, ShapeType | float | tuple[float, float]]] | dict[str, dict[str, ShapeType | float | Polygon]]
)


@dataclass
class AgentTypes:
    """Enum for agent types."""

    PEDESTRIAN = "pedestrian"
    BIKE = "bike"
    CUSTOM = "custom"


@dataclass
class ShapeTypes:
    """Enum for shape types."""

    CIRCLE = "circle"
    RECTANGLE = "rectangle"
    POLYGON = "polygon"


class PedestrianParts(Enum):
    """Enum for pedestrian parts"""

    bideltoid_breadth = auto()
    chest_depth = auto()
    height = auto()


class BikeParts(Enum):
    """Enum for bike parts"""

    length = auto()
    width = auto()
    pedestrian_radius = auto()


@dataclass
class BodyMeasures:
    """Class to store body measures dynamically based on agent type"""

    # équivalent à un constructeur avec un attribut measures de type dict[str, float] initialisé à un dictionnaire vide
    # `field` is imported from the `dataclasses` module and is used to specify default values for dataclass fields.
    # field(default_factory=dict)` ensures that each instance of the class gets its own unique empty dictionary as the default value.
    # avoid mutable (that can be changed) default arguments in Python, as they can lead to unexpected behavior.
    # Ex : e1 = BodyMeasures() e2 = BodyMeasures() e1.measures['bideltoid_breadth'] = 10 print(e2.measures) # ça me retourn {'bideltoid_breadth': 10}

    agent_type: AgentType
    measures: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        """Validates the measures based on the agent type."""
        # Determine required parts based on the agent type
        if self.agent_type == AgentTypes.PEDESTRIAN:
            required_parts = {part.name for part in PedestrianParts}
        elif self.agent_type == AgentTypes.BIKE:
            required_parts = {part.name for part in BikeParts}
        elif self.agent_type == AgentTypes.CUSTOM:
            required_parts = set()  # Custom agents have no predefined required parts
        else:
            raise ValueError(f"Unknown agent type: {self.agent_type}")

        # Validate that all required measures are present
        missing_parts = required_parts - self.measures.keys()
        if missing_parts:
            raise ValueError(f"Missing measures for {self.agent_type.value}: {', '.join(missing_parts)}")

        # Validate that no extra measures are provided
        extra_parts = self.measures.keys() - required_parts
        if extra_parts and self.agent_type != AgentTypes.CUSTOM:
            raise ValueError(f"Extra measures provided for {self.agent_type.value}: {', '.join(extra_parts)}")

    def number_of_measures(self) -> int:
        """Return the number of measures stored."""
        return len(self.measures)


@dataclass
class Shapes:
    """
    Class to store body shapes dynamically based on agent type.
       - Either you provide a dictionary of shapely shapes as input
       - or you specify the type of shape and its characteristics to create it dynamically.
    """

    shapes: SapeDataType = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the provided shapes."""
        # Validate that the provided shapes are valid Shapely objects
        for shape_name, shape in self.shapes.items():
            if not isinstance(shape.get("object"), (Point, Polygon)):
                raise ValueError(f"Invalid shape type for '{shape_name}': {type(shape.get('object'))}")

    def create_shape(self, name: str, shape_type: str, young_modulus: float, **kwargs) -> None:
        """
        Dynamically create a shape based on the specified type and characteristics.

        Args:
            name (str): The name of the shape.
            shape_type (str): The type of shape to create ('circle', 'rectangle', or 'polygon').
            young_modulus (float): Material property associated with the shape.
            **kwargs: Additional parameters required to create the specific shape.

        Raises:
            ValueError: If the shape type or required parameters are invalid.
        """
        if shape_type == ShapeTypes.CIRCLE:
            center = kwargs.get("center")
            radius = kwargs.get("radius")
            if not isinstance(center, tuple) or not isinstance(radius, (int, float)):
                raise ValueError("For a circle, 'center' must be a tuple and 'radius' must be a number.")
            self.shapes[name] = {
                "shape_type": ShapeTypes.CIRCLE,
                "young_modulus": young_modulus,
                "object": Point(center).buffer(radius),
            }

        elif shape_type == ShapeTypes.RECTANGLE:
            min_x = kwargs.get("min_x")
            min_y = kwargs.get("min_y")
            max_x = kwargs.get("max_x")
            max_y = kwargs.get("max_y")
            if not all(isinstance(coord, (int, float)) for coord in [min_x, min_y, max_x, max_y]):
                raise ValueError("For a rectangle, 'min_x', 'min_y', 'max_x', and 'max_y' must be numbers.")
            self.shapes[name] = {
                "shape_type": ShapeTypes.RECTANGLE,
                "young_modulus": young_modulus,
                "object": Polygon([(min_x, min_y), (min_x, max_y), (max_x, max_y), (max_x, min_y)]),
            }

        elif shape_type == ShapeTypes.POLYGON:
            points = kwargs.get("points")
            if not isinstance(points, list) or not all(isinstance(point, tuple) for point in points):
                raise ValueError("For a polygon, 'points' must be a list of tuples.")

            if len(points) < 3 or points[0] != points[-1]:
                raise ValueError("A polygon must have at least 3 points and the first/last points must match.")

            self.shapes[name] = {
                "shape_type": ShapeTypes.POLYGON,
                "young_modulus": young_modulus,
                "object": Polygon(points),
            }

        else:
            raise ValueError(f"Unsupported shape type: {shape_type}")

    def get_shape(self, name: str) -> dict[str, ShapeType | float | Polygon]:
        """Retrieve a shape by its name."""
        if name not in self.shapes:
            raise KeyError(f"No shape found with name '{name}'.")
        return self.shapes[name]["object"]

    def get_additional_parameters(self) -> SapeDataType:
        """
        Retrieve additional parameters for each stored shape.

        Returns:
            A dictionary containing additional parameters for each shape.
        """
        params = {}
        for name, shape in self.shapes.items():
            if shape["shape_type"] == ShapeTypes.CIRCLE:
                disk = shape["object"]
                disk_center = disk.centroid
                disk_radius = disk.exterior.distance(disk.centroid)
                params[name] = {
                    "shape_type": ShapeTypes.CIRCLE,
                    "young_modulus": shape["young_modulus"],
                    "center": (disk_center.x, disk_center.y),
                    "radius": disk_radius,
                }
            elif shape["shape_type"] == ShapeTypes.RECTANGLE:
                rect = shape["object"]
                min_x, min_y, max_x, max_y = rect.bounds
                params[name] = {
                    "shape_type": ShapeTypes.RECTANGLE,
                    "young_modulus": shape["young_modulus"],
                    "min_x": min_x,
                    "min_y": min_y,
                    "max_x": max_x,
                    "max_y": max_y,
                }
            elif shape["shape_type"] == ShapeTypes.POLYGON:
                poly = shape["object"]
                poly_points = list(poly.exterior.coords)
                params[name] = {
                    "shape_type": ShapeTypes.POLYGON,
                    "young_modulus": shape["young_modulus"],
                    "points": poly_points,
                }

        return params

    def number_of_shapes(self) -> int:
        """Return the total number of stored shapes."""
        return len(self.shapes)


class Agent:
    """Class representing an agent with physical attributes and geometry"""

    def __init__(
        self,
        sex: Sex | None,
        agent_type: AgentType,
        measures: BodyMeasures | dict[str, float],
        shapes: SapeDataType,
    ) -> None:
        # Convert dictionaries to dataclass instances if necessary
        if isinstance(measures, dict):
            measures = BodyMeasures(measures)  # Assuming BodyMeasures can be initialized from a dictionary
        elif not isinstance(measures, BodyMeasures):
            raise ValueError("`measures` should be an instance of BodyMeasures or a dictionary.")

        if isinstance(shapes, dict):
            shapes = Shapes(shapes)  # Assuming Shapes can be initialized from a dictionary
        elif not isinstance(shapes, Shapes):
            raise ValueError("`shapes` should be an instance of Shapes or a dictionary.")

        self._sex = sex
        self._agent_type = agent_type
        self._measures = measures
        self._shapes = shapes

    @property
    def sex(self) -> Sex:
        """Get the sex of the pedestrian."""
        return self._sex

    @sex.setter
    def sex(self, value: str) -> None:
        """Set a new sex for the pedestrian."""
        if value not in get_args(Sex):
            allowed_values = ", ".join(get_args(Sex))
            # Corrected error message
            raise ValueError(f"Sex should be one of: {allowed_values}.")
        self._sex = value

    @property
    def agent_type(self) -> AgentType:
        """Get the type of the agent."""
        return self._agent_type

    @agent_type.setter
    def agent_type(self, value: str) -> None:
        """Set a new type for the agent."""
        if value not in get_args(AgentType):
            allowed_values = ", ".join(get_args(AgentType))
            raise ValueError(f"Agent type should be one of: {allowed_values}.")
        self._agent_type = value

    @property
    def measures(self) -> BodyMeasures:
        """Get the body measures of the agent."""
        return self._measures

    @measures.setter
    def measures(self, value: Union[BodyMeasures, dict[str, float]]) -> None:
        """Set the body measures of the agent."""
        if isinstance(value, dict):
            value = BodyMeasures(value)
        self._measures = value

    @property
    def shapes(self) -> Shapes:
        """Get the body shapes of the agent."""
        return self._shapes

    def rotation_axis(self) -> Point:
        """Return the rotation axis of the agent in 2D"""
        return MultiPoint([shape["object"].centroid for shape in self.shapes.shapes.values()]).centroid

    def rotate(self, angle: float) -> None:
        """Rotate all shapes by a given angle around a specified axis."""
        rotation_axis = self.rotation_axis()
        for name, shape in self.shapes.shapes.items():
            shape_object = shape["object"]
            self.shapes.shapes[name]["object"] = rotate(shape_object, angle, origin=rotation_axis, use_radians=True)

    def translate(self, dx: float, dy: float) -> None:
        """Translate all shapes by given x and y offsets."""
        for name, shape in self.shapes.shapes.items():
            shape_object = shape["object"]
            self.shapes.shapes[name]["object"] = translate(shape_object, xoff=dx, yoff=dy)
