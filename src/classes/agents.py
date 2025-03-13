"""Defines classes to store physical attributes and geometry of agents."""

from typing import Optional, Union

import shapely.affinity as affin
from shapely.geometry import MultiPoint, MultiPolygon, Point, Polygon

import src.utils.constants as cst
from src.classes.measures import AgentMeasures
from src.classes.shapes2D import Shapes2D
from src.classes.shapes3D import Shapes3D
from src.utils import functions as fun
from src.utils.typing_custom import Sex, ShapeDataType, ShapeType


class Agent:
    """Class representing an agent with physical attributes and geometry."""

    def __init__(
        self,
        agent_type: cst.AgentTypes,
        measures: Union[dict[str, float | Sex], AgentMeasures],
        shapes2D: Optional[Shapes2D | ShapeDataType] = None,
        shapes3D: Optional[Shapes3D | dict[str, ShapeType | MultiPolygon]] = None,
    ) -> None:
        """Initialize an Agent instance.

        Parameters
        ----------
        agent_type : AgentType
            The type of the agent.
        measures : dict[str, float] | AgentMeasures
            The measures associated with the agent.
        shapes2D : Shapes2D | dict[str, ShapeType], optional
            The 2D shapes associated with the agent.
            Defaults to None.
        shapes3D : Shapes3D | dict[str, ShapeType | MultiPolygon], optional
            The 3D shapes associated with the agent. Defaults to None.

        Raises
        ------
        ValueError
            If any argument has invalid type or value.
        """
        self._agent_type = self._validate_agent_type(agent_type)
        self._measures = self._initialize_measures(agent_type, measures)
        self._shapes2D = self._initialize_shapes2D(agent_type, shapes2D)
        self._shapes3D = self._initialize_shapes3D(agent_type, shapes3D)

    def _validate_agent_type(self, agent_type: cst.AgentTypes) -> cst.AgentTypes:
        """
        Validate the provided agent type.

        Parameters
        ----------
        agent_type : AgentType
            The agent type to validate.

        Returns
        -------
        AgentType
            The validated agent type.

        Raises
        ------
        ValueError
            If `agent_type` is not a valid member of the `AgentType` enumeration.

        """
        if not isinstance(agent_type, cst.AgentTypes):
            raise ValueError(f"Agent type should be one of: {[member.name for member in cst.AgentTypes]}.")
        return agent_type

    def _initialize_measures(self, agent_type: cst.AgentTypes, measures: AgentMeasures | dict[str, float | Sex]) -> AgentMeasures:
        """
        Initialize measures for an agent.

        This method initializes the measures for an agent based on the provided
        input, which can either be a dictionary of measures or an `AgentMeasures`
        instance.

        Parameters
        ----------
        agent_type : AgentType
            The type of the agent for which the measures are being initialized.
        measures : dict of str to float or AgentMeasures
            The input measures. This can either be:
            - A dictionary where keys are measure names (str) and values are their
              corresponding values (float).
            - An instance of `AgentMeasures`.

        Returns
        -------
        AgentMeasures
            An `AgentMeasures` object initialized with the provided input.

        Raises
        ------
        ValueError
            If `measures` is neither a dictionary nor an instance of `AgentMeasures`.
        """
        if isinstance(measures, dict):
            return AgentMeasures(agent_type=agent_type, measures=measures)
        if isinstance(measures, AgentMeasures):
            return measures
        raise ValueError("`measures` should be an instance of AgentMeasures or a dictionary.")

    def _initialize_shapes2D(self, agent_type: cst.AgentTypes, shapes2D: Optional[Shapes2D | ShapeDataType]) -> Shapes2D:
        """Initialize 2D shapes for an agent.

        This method initializes the 2D shapes associated with an agent based on the
        provided input. If no shapes are provided, default shapes are created based
        on the agent type.

        Parameters
        ----------
        agent_type : AgentType
            The type of the agent for which the 2D shapes are being initialized.
        shapes2D : Shapes2D or dict of str to ShapeType or None, optional
            The input shapes. This can be:
            - `None` (default): Creates an empty `Shapes2D` instance for the agent.
            - A dictionary where keys are shape names (str) and values are their
            corresponding shape types (`ShapeType`).
            - An instance of `Shapes2D`.

        Returns
        -------
        Shapes2D
            A `Shapes2D` object initialized with the provided input or default shapes.

        Raises
        ------
        ValueError
            If `shapes2D` is neither `None`, a dictionary, nor an instance of `Shapes2D`.

        Notes
        -----
        If no shapes are provided (`shapes2D` is empty), default shapes will be created
        based on the agent type:
            - For pedestrians: Pedestrian-specific shapes are created using
            `create_pedestrian_shapes`.
            - For bikes: Bike-specific shapes are created using `create_bike_shapes`.
        """
        if shapes2D is None:
            shapes2D = Shapes2D(agent_type=agent_type)
        elif isinstance(shapes2D, dict):
            shapes2D = Shapes2D(agent_type=agent_type, shapes=shapes2D)
        elif not isinstance(shapes2D, Shapes2D):
            raise ValueError("`shapes2D` should be an instance of Shapes2D or a dictionary or None.")
        if not shapes2D.shapes:
            if agent_type == cst.AgentTypes.pedestrian:
                shapes2D.create_pedestrian_shapes(self._measures)
            elif agent_type == cst.AgentTypes.bike:
                shapes2D.create_bike_shapes(self._measures)
        return shapes2D

    def _initialize_shapes3D(
        self,
        agent_type: cst.AgentTypes,
        shapes3D: Optional[Shapes3D | dict[str, ShapeType | MultiPolygon]],
    ) -> Shapes3D:
        """
        Initialize the 3D shapes for the agent.

        Parameters
        ----------
        agent_type : AgentType
            The type of the agent (e.g., pedestrian, bike).
        shapes3D : Shapes3D or dict[str, ShapeType or MultiPolygon], optional
            The 3D shapes associated with the agent. If provided as a dictionary,
            it will be converted to a `Shapes3D` instance. If None, default 3D shapes
            will be initialized based on the agent type and measures.

        Returns
        -------
        Shapes3D
            The initialized 3D shapes for the agent.

        Raises
        ------
        ValueError
            If `shapes3D` is neither a dictionary, an instance of `Shapes3D`, nor None.

        """
        if shapes3D is None:
            shapes3D = Shapes3D(agent_type=agent_type)
        elif isinstance(shapes3D, dict):
            shapes3D = Shapes3D(agent_type=agent_type, shapes=shapes3D)
        elif not isinstance(shapes3D, Shapes3D):
            raise ValueError("`shapes3D` should be an instance of Shapes3D or a dictionary or None.")
        if not shapes3D.shapes:
            if agent_type == cst.AgentTypes.pedestrian:
                shapes3D.create_pedestrian3D(self._measures)
        return shapes3D

    @property
    def agent_type(self) -> cst.AgentTypes:
        """Get the type of the agent.

        Parameters
        ----------
        None

        Returns
        -------
        AgentType
            The type of the agent.

        """
        return self._agent_type

    @agent_type.setter
    def agent_type(self, value: cst.AgentTypes) -> None:
        """Set a new type for the agent.

        Parameters
        ----------
        value : AgentType
            The new type to be assigned to the agent.

        Raises
        ------
        ValueError
            If the provided value is not a valid AgentType.

        """
        if not isinstance(value, cst.AgentTypes):
            raise ValueError(f"Agent type should be one of: {[member.name for member in cst.AgentTypes]}.")
        self._agent_type = value

    @property
    def measures(self) -> AgentMeasures:
        """Retrieve the body measures of the agent.

        Parameters
        ----------
        None

        Returns
        -------
        AgentMeasures
            An object containing the body measures of the agent.

        """
        return self._measures

    @measures.setter
    def measures(self, value: AgentMeasures | dict[str, float | Sex]) -> None:
        """Set the body measures of the agent.

        Parameters
        ----------
        value : AgentMeasures | dict[str, float]
            The body measures of the agent.
            If a dictionary is provided, it will be converted to an AgentMeasures instance.

        Returns
        -------
        None

        """
        if self.agent_type == cst.AgentTypes.pedestrian:
            if isinstance(value, dict):
                value = AgentMeasures(agent_type=cst.AgentTypes.pedestrian, measures=value)
            self._measures = value
            self.shapes2D.create_pedestrian_shapes(self._measures)
            if self.shapes3D is not None:
                self.shapes3D.create_pedestrian3D(self._measures)
            else:
                self.shapes3D = Shapes3D(agent_type=cst.AgentTypes.pedestrian)
                self.shapes3D.create_pedestrian3D(self._measures)
        if self.agent_type == cst.AgentTypes.bike:
            if isinstance(value, dict):
                value = AgentMeasures(agent_type=cst.AgentTypes.bike, measures=value)
            self._measures = value
            self.shapes2D.create_bike_shapes(self._measures)

    @property
    def shapes2D(self) -> Shapes2D:
        """Retrieve the 2D body shapes of the agent.

        Parameters
        ----------
        None

        Returns
        -------
        Shapes2D
            An instance representing the 2D shapes of the agent's body.

        """
        return self._shapes2D

    @shapes2D.setter
    def shapes2D(self, value: Shapes2D | ShapeDataType) -> None:
        """Set the body shapes of the agent.

        Parameters
        ----------
        value : Shapes2D | dict[str, ShapeType | float | Polygon]
            The shapes to set for the agent.
            This can either be an instance of Shapes2D or a dictionary where the keys are strings
            and the values are either ShapeType, float, or Polygon.

        Returns
        -------
        None

        """
        if isinstance(value, dict):
            value = Shapes2D(agent_type=self.agent_type, shapes=value)
        self._shapes2D = value

    @property
    def shapes3D(self) -> Shapes3D | None:
        """Get the 3D body shapes of the agent.

        Parameters
        ----------
        None

        Returns
        -------
        Shapes3D | None
            The 3D body shapes of the agent if available, otherwise None.

        """
        return self._shapes3D

    @shapes3D.setter
    def shapes3D(self, value: Shapes3D | dict[str, ShapeType | MultiPolygon]) -> None:
        """Set the 3D body shapes of the agent.

        Parameters
        ----------
        value : Shapes3D | dict[str, ShapeType | MultiPolygon]
            The 3D shapes to set.
            If a dictionary is provided, it will be converted to a Shapes3D object.

        Returns
        -------
        None

        """
        if isinstance(value, dict):
            value = Shapes3D(agent_type=self.agent_type, shapes=value)
        self._shapes3D = value

    def translate(self, dx: float, dy: float) -> None:
        """Translate all shapes by given x and y offsets.

        Parameters
        ----------
        dx : float
            The offset to translate along the x-axis.
        dy : float
            The offset to translate along the y-axis.

        Returns
        -------
        None

        """
        for name, shape in self.shapes2D.shapes.items():
            shape_object = shape["object"]
            self.shapes2D.shapes[name]["object"] = affin.translate(shape_object, xoff=dx, yoff=dy)

    def rotate(self, angle: float) -> None:
        """Rotate all shapes by a given angle around a specified axis.

        This method rotates all the shapes in the `shapes2D` attribute by the specified angle.
        The rotation is performed around the centroid of all shapes combined.

        Parameters
        ----------
        angle : float
            The angle in degrees by which to rotate the shapes.

        Returns
        -------
        None

        """
        rotation_axis = self.get_position()
        for name, shape in self.shapes2D.shapes.items():
            shape_object = shape["object"]
            self.shapes2D.shapes[name]["object"] = affin.rotate(shape_object, angle, origin=rotation_axis, use_radians=False)
        self.shapes2D.reference_direction = fun.wrap_angle(self.shapes2D.reference_direction + angle)

    def get_position(self) -> Point:
        """Get the position of the agent.

        This method calculates the centroid of all the 2D shapes associated with the agent
        and returns it as a Point object.

        Parameters
        ----------
        None

        Returns
        -------
        Point
            The centroid of all the 2D shapes.

        """
        multipoint = []
        for shape in self.shapes2D.shapes.values():
            if isinstance(shape["object"], (MultiPolygon, Polygon)):
                multipoint.append(shape["object"].centroid)
        return MultiPoint(multipoint).centroid

    def get_orientation(self) -> float:
        """Get the orientation of the agent.

        Parameters
        ----------
        None

        Returns
        -------
        float
            The orientation of the agent in degrees or radians, depending on the implementation.

        """
        return self.shapes2D.reference_direction

    def translate_body3D(self, dx: float, dy: float, dz: float) -> None:
        """Translate the 3D body of the pedestrian by the specified displacements dx, dy, and dz.

        Parameters
        ----------
        dx : float
            The displacement along the x-axis.
        dy : float
            The displacement along the y-axis.
        dz : float
            The displacement along the z-axis.

        Returns
        -------
        None

        """
        translated_body3D: ShapeDataType = {}
        if self.shapes3D is None:
            raise ValueError("No 3D shapes available for the agent.")
        for height, multipolygon in self.shapes3D.shapes.items():
            translated_body3D[f"{float(height) + dz}"] = affin.translate(multipolygon, dx, dy)
        self.shapes3D.shapes = translated_body3D

    def rotate_body3D(self, angle: float) -> None:
        """Rotates the 3D body of the pedestrian by the specified angle in radians.

        This method updates the `shapes3D` attribute of the pedestrian by rotating
        each 3D shape around the centroid of all shapes combined. The rotation is
        performed in the 2D plane.

        Parameters
        ----------
        angle : float
            The angle by which to rotate the 3D body, in radians.

        Returns
        -------
        None

        """
        rotated_body3D = {}
        centroid_body = []
        if self.shapes3D is None:
            raise ValueError("No 3D shapes available for the agent.")
        for multipolygon in self.shapes3D.shapes.values():
            if isinstance(multipolygon, (MultiPolygon, Polygon)):
                centroid_body.append(multipolygon.centroid)
        centroid_body = MultiPoint(centroid_body).centroid
        for height, multipolygon in self.shapes3D.shapes.items():
            rotated_body3D[height] = affin.rotate(multipolygon, angle, origin=centroid_body, use_radians=False)
        self.shapes3D.shapes = rotated_body3D
