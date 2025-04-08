"""Defines classes to store physical attributes and geometry of agents."""

import numpy as np
import shapely.affinity as affin
from numpy.typing import NDArray
from shapely.geometry import MultiPoint, MultiPolygon, Point, Polygon

import configuration.utils.constants as cst
from configuration.models.measures import AgentMeasures
from configuration.models.shapes2D import Shapes2D
from configuration.models.shapes3D import Shapes3D
from configuration.utils import functions as fun
from configuration.utils.typing_custom import Sex, ShapeDataType, ShapeType


class Agent:
    """
    Class representing an agent with physical attributes and geometry.

    Parameters
    ----------
    agent_type : AgentTypes
        The type of the agent.
    measures : dict[str, float | Sex] | AgentMeasures
        The measures associated with the agent. Can be a dictionary with measure
        names as keys and float values or Sex (Literal["male","female"]), or an AgentMeasures object.
    shapes2D : Shapes2D | ShapeDataType
        The 2D shapes associated with the agent. Can be a Shapes2D object or a
        dictionary of shape data. Default is None.
    shapes3D : Shapes3D | dict[float, ShapeType | MultiPolygon]
        The 3D shapes associated with the agent. Can be a Shapes3D object or a
        dictionary with float keys and ShapeType or MultiPolygon values. Default is None.
    """

    def __init__(
        self,
        agent_type: cst.AgentTypes,
        measures: dict[str, float | Sex] | AgentMeasures,
        shapes2D: Shapes2D | ShapeDataType | None = None,
        shapes3D: Shapes3D | dict[float, ShapeType | MultiPolygon] | None = None,
    ) -> None:
        """
        Initialize an Agent instance.

        Parameters
        ----------
        agent_type : AgentTypes
            The type of the agent.
        measures : dict[str, float | Sex] | AgentMeasures
            The measures associated with the agent. Can be a dictionary with measure
            names as keys and float values or Sex (Literal["male","female"]), or an AgentMeasures object.
        shapes2D : Shapes2D | ShapeDataType
            The 2D shapes associated with the agent. Can be a Shapes2D object or a
            dictionary of shape data. Default is None.
        shapes3D : Shapes3D | dict[float, ShapeType | MultiPolygon]
            The 3D shapes associated with the agent. Can be a Shapes3D object or a
            dictionary with float keys and ShapeType or MultiPolygon values. Default is None.

        Raises
        ------
        ValueError
            If any argument has invalid type or value.
        """
        self._agent_type = self._validate_agent_type(agent_type)
        self._measures = self._initialize_measures(agent_type, measures)
        self._shapes2D = self._initialize_shapes2D(agent_type, shapes2D)
        self._shapes3D = self._initialize_shapes3D(agent_type, shapes3D)

        if self._shapes2D.shapes:
            # Compute the moment of inertia of the agent being created
            self._measures.measures[cst.CommonMeasures.moment_of_inertia.name] = fun.compute_moment_of_inertia(
                self._shapes2D.get_geometric_shape(),
                self._measures.measures[cst.CommonMeasures.weight.name],
            )

    def _validate_agent_type(self, agent_type: cst.AgentTypes) -> cst.AgentTypes:
        """
        Validate the provided agent type.

        Parameters
        ----------
        agent_type : AgentTypes
            The agent type to validate. Must be a member of the AgentTypes enumeration.

        Returns
        -------
        AgentTypes
            The validated agent type.

        Raises
        ------
        ValueError
            If `agent_type` is not a valid member of the AgentTypes enumeration.
        """
        if not isinstance(agent_type, cst.AgentTypes):
            raise ValueError(f"Agent type should be one of: {[member.name for member in cst.AgentTypes]}.")
        return agent_type

    def _initialize_measures(self, agent_type: cst.AgentTypes, measures: AgentMeasures | dict[str, float | Sex]) -> AgentMeasures:
        """
        Initialize measures for an agent.

        Parameters
        ----------
        agent_type : AgentTypes
            The type of the agent for which the measures are being initialized.
        measures : AgentMeasures or dict[str, float | Sex]
            The input measures. This can either be:
                - A dictionary where keys are measure names (str) and values are their
                corresponding values (float or Sex).
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

    def _initialize_shapes2D(self, agent_type: cst.AgentTypes, shapes2D: Shapes2D | ShapeDataType | None) -> Shapes2D:
        """
        Initialize 2D shapes for an agent.

        Parameters
        ----------
        agent_type : AgentTypes
            The type of the agent for which the 2D shapes are being initialized.
        shapes2D : Shapes2D | ShapeDataType
            The input shapes. This can be:
                - None (default): Creates an empty `Shapes2D` instance for the agent.
                - A dictionary (ShapeDataType) where keys are shape names (str) and
                    values are their corresponding shape types (ShapeType).
                - An instance of `Shapes2D`.

        Returns
        -------
        Shapes2D
            A `Shapes2D` object initialized with the provided input or default shapes.

        Raises
        ------
        ValueError
            If `shapes2D` is neither None, a dictionary, nor an instance of `Shapes2D`.

        Notes
        -----
        - If `shapes2D` is None, an empty `Shapes2D` instance is created.
        - If `shapes2D` is a dictionary, it's used to create a new `Shapes2D` instance.
        - If `shapes2D` is already a `Shapes2D` instance, it's used as-is.
        - If no shapes are provided (empty `Shapes2D`), default shapes are created
          based on the agent type:
            - For pedestrians: `create_pedestrian_shapes` is called.
            - For bikes: `create_bike_shapes` is called.
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
        shapes3D: Shapes3D | dict[float, ShapeType | MultiPolygon],
    ) -> Shapes3D:
        """
        Initialize the 3D shapes for the agent.

        Parameters
        ----------
        agent_type : AgentTypes
            The type of the agent (e.g., pedestrian, bike).
        shapes3D : Shapes3D | dict[float, ShapeType | MultiPolygon]
            The 3D shapes input. Can be:
                - None: Creates an empty `Shapes3D` instance
                - Dictionary: Keys are sllice height (float), values are `ShapeType` or `MultiPolygon`
                - `Shapes3D` instance
            Default is None.

        Returns
        -------
        Shapes3D
            Initialized 3D shapes for the agent. Returns:
                - Empty `Shapes3D` if input is None
                - New `Shapes3D` from dict if input is dictionary
                - Original `Shapes3D` if input is already instance

        Raises
        ------
        ValueError
            If `shapes3D` is not None, dict, or Shapes3D instance.
        """
        if shapes3D is None:
            shapes3D = Shapes3D(agent_type=agent_type)
        elif isinstance(shapes3D, dict):
            shapes3D = Shapes3D(agent_type=agent_type, shapes=shapes3D)
        elif not isinstance(shapes3D, Shapes3D):
            raise ValueError("`shapes3D` should be an instance of Shapes3D or a dictionary or None.")
        if isinstance(shapes3D, Shapes3D) and not shapes3D.shapes:
            if agent_type == cst.AgentTypes.pedestrian:
                shapes3D.create_pedestrian3D(self._measures)
        return shapes3D

    @property
    def agent_type(self) -> cst.AgentTypes:
        """
        Get the agent type.

        Returns
        -------
        AgentType
            The current agent type from the enumeration of valid types.
        """
        return self._agent_type

    @agent_type.setter
    def agent_type(self, value: cst.AgentTypes) -> None:
        """
        Set a new agent type with validation.

        Parameters
        ----------
        value : AgentTypes
            New agent type to assign. Must be a valid member of the AgentTypes enumeration.

        Raises
        ------
        ValueError
            If input is not a valid member of AgentTypes.
        """
        if not isinstance(value, cst.AgentTypes):
            raise ValueError(f"Agent type should be one of: {[member.name for member in cst.AgentTypes]}.")
        self._agent_type = value

    @property
    def measures(self) -> AgentMeasures:
        """
        Access the agent's physical measurement data.

        Returns
        -------
        AgentMeasures
            Dataclass object holding all measurement parameters including
            weight, dimensions, and biological characteristics.
        """
        return self._measures

    @measures.setter
    def measures(self, value: AgentMeasures | dict[str, float | Sex]) -> None:
        """
        Update agent measurements and regenerate associated shapes.

        Parameters
        ----------
        value : AgentMeasures | dict[str, float | Sex]
            New measurements to apply. Accepts either:
                - Prepared AgentMeasures instance
                - Raw measurement dictionary (converted to AgentMeasures)

        Raises
        ------
        TypeError
            If input type is neither AgentMeasures nor dictionary
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
        """
        Access the agent's 2D representation.

        Returns
        -------
        Shapes2D
            Dataclass object holding all 2D shapes defining the agent's
            spatial boundaries.
        """
        return self._shapes2D

    @shapes2D.setter
    def shapes2D(self, value: Shapes2D | ShapeDataType) -> None:
        """
        Update the agent's 2D geometric configuration.

        Parameters
        ----------
        value : Shapes2D | ShapeDataType
            New 2D shape configuration. Can be:
                - Shapes2D instance
                - Dictionary: Shape definitions (str keys with ShapeType/Polygon/float values)

        Raises
        ------
        TypeError
            If input cannot initialize a valid Shapes2D object
        """
        if isinstance(value, dict):
            value = Shapes2D(agent_type=self.agent_type, shapes=value)
        self._shapes2D = value

    @property
    def shapes3D(self) -> Shapes3D | None:
        """
        Access the agent's 3D geometric representations.

        Returns
        -------
        Shapes3D or None
            Dataclass object holding all 3D shapes defining the agent's
            3D features, if available. None if not set.
        """
        return self._shapes3D

    @shapes3D.setter
    def shapes3D(self, value: Shapes3D | dict[float, ShapeType | MultiPolygon]) -> None:
        """
        Update the agent's 3D geometric configuration.

        Parameters
        ----------
        value : Shapes3D | dict[float, ShapeType | MultiPolygon]
            New 3D shape configuration. Can be:
            - Shapes3D instance: Used directly
            - Dictionary: Shape definitions (float keys with ShapeType/MultiPolygon values)

        Raises
        ------
        TypeError
            If input cannot initialize a valid Shapes3D object
        """
        if isinstance(value, dict):
            value = Shapes3D(agent_type=self.agent_type, shapes=value)
        self._shapes3D = value

    def translate(self, dx: float, dy: float) -> None:
        """
        Translate all 2D shapes by specified offsets in x and y directions.

        Parameters
        ----------
        dx : float
            Translation offset along the x-axis in centimeters units.
        dy : float
            Translation offset along the y-axis in centimeters units.

        Notes
        -----
        - Modifies all 2D shapes in place
        - Does not affect 3D shapes (see `shapes3D` property for 3D transformations)
        """
        for name, shape in self.shapes2D.shapes.items():
            shape_object = shape["object"]
            self.shapes2D.shapes[name]["object"] = affin.translate(shape_object, xoff=dx, yoff=dy)

    def rotate(self, angle: float) -> None:
        """
        Rotate all 2D shapes around their combined centroid by specified angle.

        Parameters
        ----------
        angle : float
            Rotation angle in degrees (positive for counter-clockwise).
        """
        rotation_axis = self.get_position()
        for name, shape in self.shapes2D.shapes.items():
            shape_object = shape["object"]
            self.shapes2D.shapes[name]["object"] = affin.rotate(shape_object, angle, origin=rotation_axis, use_radians=False)

    def get_position(self) -> Point:
        """
        Calculate the agent's position based on 2D shape geometry.

        Returns
        -------
        Point
            Geometric centroid of all polygon-based 2D shapes, calculated as:
                1. Extract centroids from all Polygon/MultiPolygon shapes
                2. Create MultiPoint from these centroids
                3. Return centroid of this MultiPoint
        """
        multipoint = []
        for shape in self.shapes2D.shapes.values():
            if isinstance(shape["object"], (MultiPolygon, Polygon)):
                multipoint.append(shape["object"].centroid)
        return MultiPoint(multipoint).centroid

    def translate_body3D(self, dx: float, dy: float, dz: float) -> None:
        """
        Translate 3D shapes along all spatial axes with height adjustment.

        Parameters
        ----------
        dx : float
            Displacement along x-axis in centimeter units.
        dy : float
            Displacement along y-axis in centimeter units.
        dz : float
            Vertical displacement along the z-axis in centimeter units, modifying height keys in shapes3D.

        Raises
        ------
        ValueError
            If shapes3D is None or contains no 3D shapes.
        """
        translated_body3D: ShapeDataType = {}
        if self.shapes3D is None:
            raise ValueError("No 3D shapes available for the agent.")
        for height, multipolygon in self.shapes3D.shapes.items():
            translated_body3D[float(height) + dz] = affin.translate(multipolygon, dx, dy)
        self.shapes3D.shapes = translated_body3D

    def rotate_body3D(self, angle: float) -> None:
        """
        Rotate all 3D shapes on XY plane around Z-axis.

        Parameters
        ----------
        angle : float
            Rotation angle in degrees (positive counter-clockwise).

        Raises
        ------
        ValueError
            If shapes3D is None or contains no rotatable shapes.
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

    def get_delta_GtoGi(self) -> dict[str, tuple[float, float]]:
        """
        Give the position vector from the agent centroid to the centroid of each shape.

        Returns
        -------
        dict[str, tuple[float, float]]
            Dictionary with shape names as keys and tuples of x and y coordinates
            as values, representing the position vector from the agent centroid to
            the centroid of each shape.
        """
        delta_GtoGi = {}
        agent_center: Point = self.get_position()
        for name, shape in self.shapes2D.shapes.items():
            shape_center_x: float = shape["object"].centroid.x
            shape_center_y: float = shape["object"].centroid.y
            delta_GtoGi[name] = (shape_center_x - agent_center.x, shape_center_y - agent_center.y)
        return delta_GtoGi

    def get_agent_orientation(self) -> float:
        """
        Get the agent's orientation angle as the direction of delta_GtoG0 - delta_GtoG-1 (the first shape minus the last shape).

        Returns
        -------
        float
            The angle of the agent in degrees.
        """
        delta_GtoGi: dict[str, tuple[float, float]] = self.get_delta_GtoGi()
        delta_GtoG0: NDArray[np.float64] = np.array(delta_GtoGi["disk0"])
        delta_GtoG4: NDArray[np.float64] = np.array(delta_GtoGi["disk4"])
        shoulders_direction: NDArray[np.float64] = (delta_GtoG0 - delta_GtoG4) / np.linalg.norm(delta_GtoG0 - delta_GtoG4)
        head_orientation: float = np.arctan2(shoulders_direction[1], shoulders_direction[0]) - np.pi / 2
        head_orientation_degrees: float = fun.wrap_angle(np.degrees(head_orientation))
        return head_orientation_degrees
