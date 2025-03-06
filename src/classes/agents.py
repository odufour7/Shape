"""This module defines classes to store physical attributes and geometry of agents."""

from typing import get_args

from shapely.affinity import rotate, translate
from shapely.geometry import MultiPoint, MultiPolygon, Point, Polygon

import src.utils.constants as cst
from src.classes.measures import AgentMeasures
from src.classes.shapes2D import Shapes2D
from src.classes.shapes3D import Shapes3D
from src.utils import functions as fun
from src.utils.typing_custom import AgentType, ShapeType


class Agent:
    """Class representing an agent with physical attributes and geometry"""

    def __init__(
        self,
        agent_type: AgentType,
        measures: dict[str, float] | AgentMeasures,
        shapes2D: Shapes2D = None,
        shapes3D: Shapes3D | dict[str, ShapeType | MultiPolygon] = None,
    ) -> None:
        # Convert dictionaries to dataclass instances if necessary
        if agent_type not in get_args(AgentType):
            allowed_values = ", ".join(get_args(AgentType))
            raise ValueError(f"Agent type should be one of: {allowed_values}.")

        if isinstance(measures, dict):
            measures = AgentMeasures(measures)  # Assuming Measures can be initialized from a dictionary
        elif not isinstance(measures, AgentMeasures):
            raise ValueError("`measures` should be an instance of Measures or a dictionary.")

        if isinstance(shapes2D, dict):
            shapes2D = Shapes2D(agent_type=agent_type, shapes=shapes2D)
        if shapes2D is None:
            shapes2D = Shapes2D(agent_type=agent_type)
        if isinstance(shapes2D, Shapes2D) and not shapes2D.shapes:
            if agent_type == cst.AgentTypes.pedestrian.name:
                shapes2D.create_pedestrian_shapes(measures)
            elif agent_type == cst.AgentTypes.bike.name:
                shapes2D.create_bike_shapes(measures)
        if not isinstance(shapes2D, Shapes2D):
            raise ValueError("`shapes2D` should be an instance of Shapes2D or a dictionary or None.")

        if isinstance(shapes3D, dict):
            shapes3D = Shapes3D(agent_type=agent_type, shapes=shapes3D)
        if shapes3D is None:
            shapes3D = Shapes3D(agent_type=agent_type)
        if isinstance(shapes3D, Shapes3D) and not shapes3D.shapes:
            if agent_type == cst.AgentTypes.pedestrian.name:
                shapes3D.create_pedestrian3D(measures)
        if not isinstance(shapes3D, Shapes3D):
            raise ValueError("`shapes3D` should be an instance of Shapes3D or a dictionary or None.")

        self._agent_type: AgentType = agent_type
        self._measures: AgentMeasures = measures
        self._shapes2D: Shapes2D = shapes2D
        self._shapes3D: Shapes3D = shapes3D

    @property
    def agent_type(self) -> AgentType:
        """Get the type of the agent."""
        return self._agent_type

    @agent_type.setter
    def agent_type(self, value: AgentType) -> None:
        """Set a new type for the agent."""
        if value not in get_args(AgentType):
            allowed_values = ", ".join(get_args(AgentType))
            raise ValueError(f"Agent type should be one of: {allowed_values}.")
        self._agent_type = value

    @property
    def measures(self) -> AgentMeasures:
        """Get the body measures of the agent."""
        return self._measures

    @measures.setter
    def measures(self, value: AgentMeasures | dict[str, float]) -> None:
        """Set the body measures of the agent."""
        if isinstance(value, dict):
            value = AgentMeasures(value)
        self._measures = value
        if self.agent_type == cst.AgentTypes.pedestrian.name:
            self.shapes2D.create_pedestrian_shapes(self._measures)
            self.shapes3D.create_pedestrian3D(self._measures)
        if self.agent_type == cst.AgentTypes.bike.name:
            self.shapes2D.create_bike_shapes(self._measures)

    @property
    def shapes2D(self) -> Shapes2D:
        """Get the body shapes of the agent."""
        return self._shapes2D

    @shapes2D.setter
    def shapes2D(self, value: Shapes2D | dict[str, ShapeType | float | Polygon]) -> None:
        """Set the body shapes of the agent."""
        if isinstance(value, dict):
            value = Shapes2D(value)
        self._shapes2D = value

    @property
    def shapes3D(self) -> Shapes3D | None:
        """Get the 3D body shapes of the agent."""
        return self._shapes3D

    @shapes3D.setter
    def shapes3D(self, value: Shapes3D | dict[str, ShapeType | MultiPolygon]) -> None:
        """Set the 3D body shapes of the agent."""
        if isinstance(value, dict):
            value = Shapes3D(value)
        self._shapes3D = value

    def translate(self, dx: float, dy: float) -> None:
        """Translate all shapes by given x and y offsets."""
        for name, shape in self.shapes2D.shapes.items():
            shape_object = shape["object"]
            self.shapes2D.shapes[name]["object"] = translate(shape_object, xoff=dx, yoff=dy)

    def rotate(self, angle: float) -> None:
        """Rotate all shapes by a given angle given in degree around a specified axis."""
        rotation_axis = MultiPoint([shape["object"].centroid for shape in self.shapes2D.shapes.values()]).centroid
        for name, shape in self.shapes2D.shapes.items():
            shape_object = shape["object"]
            self.shapes2D.shapes[name]["object"] = rotate(shape_object, angle, origin=rotation_axis, use_radians=False)
        self.shapes2D.reference_direction = fun.wrap_angle(self.shapes2D.reference_direction + angle)

    def get_position(self) -> Point:
        """Get the position of the agent."""
        return MultiPoint([shape["object"].centroid for shape in self.shapes2D.shapes.values()]).centroid

    def get_orientation(self) -> float:
        """Get the orientation of the agent."""
        return self.shapes2D.reference_direction

    def translate_body3D(self, dx: float, dy: float, dz: float) -> None:
        """Translates the 3D body of the pedestrian by the specified displacements dx, dy, and dz."""
        translated_body3D = {}
        for height, multipolygon in self.shapes3D.shapes.items():
            translated_body3D[height + dz] = translate(multipolygon, dx, dy)
        self.shapes3D.shapes = translated_body3D

    def rotate_body3D(self, angle: float) -> None:
        """Rotates the 3D body of the pedestrian by the specified angle in radian."""
        rotated_body3D = {}
        centroid_body = MultiPoint([multipolygon.centroid for multipolygon in self.shapes3D.shapes.values()]).centroid
        for height, multipolygon in self.shapes3D.shapes.items():
            rotated_body3D[height] = rotate(multipolygon, angle, origin=centroid_body, use_radians=False)
        self.shapes3D.shapes = rotated_body3D
