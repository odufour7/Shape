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
        """
        Initialize an Agent instance.

        Args:
            agent_type (AgentType): The type of the agent.
            measures (dict[str, float] | AgentMeasures): The measures associated with the agent.
            shapes2D (Shapes2D, optional): The 2D shapes associated with the agent. Defaults to None.
            shapes3D (Shapes3D | dict[str, ShapeType | MultiPolygon], optional): The 3D shapes associated with the agent. Defaults to None.

        Raises:
            ValueError: If `agent_type` is not a valid AgentType.
            ValueError: If `measures` is neither a dictionary nor an instance of AgentMeasures.
            ValueError: If `shapes2D` is neither a dictionary, an instance of Shapes2D, nor None.
            ValueError: If `shapes3D` is neither a dictionary, an instance of Shapes3D, nor None.
        """

        # Convert dictionaries to dataclass instances if necessary
        if agent_type not in get_args(AgentType):
            allowed_values = ", ".join(get_args(AgentType))
            raise ValueError(f"Agent type should be one of: {allowed_values}.")

        # Convert dictionaries to dataclass instances if necessary
        if isinstance(measures, dict):
            measures = AgentMeasures(measures)
        # Check if measures is an instance of AgentMeasures
        elif not isinstance(measures, AgentMeasures):
            raise ValueError("`measures` should be an instance of Measures or a dictionary.")

        # Convert dictionaries to dataclass instances if necessary
        if isinstance(shapes2D, dict):
            shapes2D = Shapes2D(agent_type=agent_type, shapes=shapes2D)
        if shapes2D is None:
            shapes2D = Shapes2D(agent_type=agent_type)
        # Check if shapes2D is an instance of Shapes2D
        if isinstance(shapes2D, Shapes2D) and not shapes2D.shapes:
            if agent_type == cst.AgentTypes.pedestrian.name:
                shapes2D.create_pedestrian_shapes(measures)
            elif agent_type == cst.AgentTypes.bike.name:
                shapes2D.create_bike_shapes(measures)
        if not isinstance(shapes2D, Shapes2D):
            raise ValueError("`shapes2D` should be an instance of Shapes2D or a dictionary or None.")

        # Convert dictionaries to dataclass instances if necessary
        if isinstance(shapes3D, dict):
            shapes3D = Shapes3D(agent_type=agent_type, shapes=shapes3D)
        if shapes3D is None:
            shapes3D = Shapes3D(agent_type=agent_type)
        # Check if shapes3D is an instance of Shapes3D
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
        """
        Get the type of the agent.

        Returns:
            AgentType: The type of the agent.
        """

        return self._agent_type

    @agent_type.setter
    def agent_type(self, value: AgentType) -> None:
        """
        Set a new type for the agent.

        Parameters:
            value (AgentType): The new type to be assigned to the agent.

        Raises:
            ValueError: If the provided value is not a valid AgentType.
        """

        if value not in get_args(AgentType):
            allowed_values = ", ".join(get_args(AgentType))
            raise ValueError(f"Agent type should be one of: {allowed_values}.")
        self._agent_type = value

    @property
    def measures(self) -> AgentMeasures:
        """
        Retrieve the body measures of the agent.

        Returns:
            AgentMeasures: An object containing the body measures of the agent.
        """

        return self._measures

    @measures.setter
    def measures(self, value: AgentMeasures | dict[str, float]) -> None:
        """
        Set the body measures of the agent.

        Parameters:
            value (AgentMeasures | dict[str, float]): The body measures of the agent.
                If a dictionary is provided, it will be converted to an AgentMeasures instance.

        Returns:
            None
        """

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
        """
        Retrieve the 2D body shapes of the agent.

        Returns:
            Shapes2D: An instance representing the 2D shapes of the agent's body.
        """

        return self._shapes2D

    @shapes2D.setter
    def shapes2D(self, value: Shapes2D | dict[str, ShapeType | float | Polygon]) -> None:
        """
        Set the body shapes of the agent.

        Parameters:
            value (Shapes2D | dict[str, ShapeType | float | Polygon]): The shapes to set for the agent.
                This can either be an instance of Shapes2D or a dictionary where the keys are strings
                and the values are either ShapeType, float, or Polygon.

        Returns:
            None
        """

        if isinstance(value, dict):
            value = Shapes2D(value)
        self._shapes2D = value

    @property
    def shapes3D(self) -> Shapes3D | None:
        """
        Get the 3D body shapes of the agent.

        Returns:
            Shapes3D | None: The 3D body shapes of the agent if available, otherwise None.
        """

        return self._shapes3D

    @shapes3D.setter
    def shapes3D(self, value: Shapes3D | dict[str, ShapeType | MultiPolygon]) -> None:
        """
        Set the 3D body shapes of the agent.

        Parameters:
            value (Shapes3D | dict[str, ShapeType | MultiPolygon]): The 3D shapes to set.
                If a dictionary is provided, it will be converted to a Shapes3D object.

        Returns:
            None
        """

        if isinstance(value, dict):
            value = Shapes3D(value)
        self._shapes3D = value

    def translate(self, dx: float, dy: float) -> None:
        """
        Translate all shapes by given x and y offsets.

        Parameters:
            dx (float): The offset to translate along the x-axis.
            dy (float): The offset to translate along the y-axis.

        Returns:
            None
        """

        for name, shape in self.shapes2D.shapes.items():
            shape_object = shape["object"]
            self.shapes2D.shapes[name]["object"] = translate(shape_object, xoff=dx, yoff=dy)

    def rotate(self, angle: float) -> None:
        """
        Rotate all shapes by a given angle around a specified axis.

        This method rotates all the shapes in the `shapes2D` attribute by the specified angle.
        The rotation is performed around the centroid of all shapes combined.

        Parameters:
            angle (float): The angle in degrees by which to rotate the shapes.

        Returns:
            None
        """

        rotation_axis = MultiPoint([shape["object"].centroid for shape in self.shapes2D.shapes.values()]).centroid
        for name, shape in self.shapes2D.shapes.items():
            shape_object = shape["object"]
            self.shapes2D.shapes[name]["object"] = rotate(shape_object, angle, origin=rotation_axis, use_radians=False)
        self.shapes2D.reference_direction = fun.wrap_angle(self.shapes2D.reference_direction + angle)

    def get_position(self) -> Point:
        """
        Get the position of the agent.

        This method calculates the centroid of all the 2D shapes associated with the agent
        and returns it as a Point object.

        Returns:
            Point: The centroid of all the 2D shapes.
        """

        return MultiPoint([shape["object"].centroid for shape in self.shapes2D.shapes.values()]).centroid

    def get_orientation(self) -> float:
        """
        Get the orientation of the agent.

        Returns:
            float: The orientation of the agent in degrees or radians, depending on the implementation.
        """

        return self.shapes2D.reference_direction

    def translate_body3D(self, dx: float, dy: float, dz: float) -> None:
        """
        Translates the 3D body of the pedestrian by the specified displacements dx, dy, and dz.

        Parameters:
            dx (float): The displacement along the x-axis.
            dy (float): The displacement along the y-axis.
            dz (float): The displacement along the z-axis.

        Returns:
            None
        """

        translated_body3D = {}
        for height, multipolygon in self.shapes3D.shapes.items():
            translated_body3D[height + dz] = translate(multipolygon, dx, dy)
        self.shapes3D.shapes = translated_body3D

    def rotate_body3D(self, angle: float) -> None:
        """
        Rotates the 3D body of the pedestrian by the specified angle in radians.

        This method updates the `shapes3D` attribute of the pedestrian by rotating
        each 3D shape around the centroid of all shapes combined. The rotation is
        performed in the 2D plane.

        Parameters:
            angle (float): The angle by which to rotate the 3D body, in radians.

        Returns:
            None
        """

        rotated_body3D = {}
        centroid_body = MultiPoint([multipolygon.centroid for multipolygon in self.shapes3D.shapes.values()]).centroid
        for height, multipolygon in self.shapes3D.shapes.items():
            rotated_body3D[height] = rotate(multipolygon, angle, origin=centroid_body, use_radians=False)
        self.shapes3D.shapes = rotated_body3D
