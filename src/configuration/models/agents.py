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
    """

    def __init__(
        self,
        agent_type: cst.AgentTypes,
        measures: dict[str, float | Sex] | AgentMeasures,
    ) -> None:
        """
        Initialize an Agent instance.

        Parameters
        ----------
        agent_type : AgentTypes
            The type of the agent.
        measures : dict[str, float | Sex] | AgentMeasures
            The measures associated with the agent.

        Raises
        ------
        ValueError
            If any argument has invalid type or value.
        """
        self._agent_type = self._validate_agent_type(agent_type)
        self._measures = self._initialize_measures(agent_type, measures)
        self._shapes2D = self._initialize_shapes2D(agent_type)
        self._shapes3D = self._initialize_shapes3D(agent_type)

        if self._shapes2D.shapes:
            # Compute the moment of inertia of the agent being created
            self._measures.measures[cst.CommonMeasures.moment_of_inertia.name] = fun.compute_moment_of_inertia(
                self._shapes2D.get_geometric_shape(),
                self._measures.measures[cst.CommonMeasures.weight.name],
            )

            # Set the initial orientation of the shapes2D to 0.0°
            centroids = [
                s["object"].centroid for s in self._shapes2D.shapes.values() if isinstance(s["object"], (MultiPolygon, Polygon))
            ]
            shapes2D_centroid = MultiPoint(centroids).centroid
            for name, shape in self._shapes2D.shapes.items():
                self._shapes2D.shapes[name]["object"] = affin.rotate(shape["object"], -90, origin=shapes2D_centroid, use_radians=False)
                self._shapes2D.shapes[name]["object"] = affin.translate(
                    self._shapes2D.shapes[name]["object"], xoff=-shapes2D_centroid.x, yoff=-shapes2D_centroid.y
                )

        # Set the initial orientation of the shapes3D to 0.0°
        if self._shapes3D.shapes:
            centroids = [mp.centroid for mp in self._shapes3D.shapes.values() if isinstance(mp, (MultiPolygon, Polygon))]
            centroid_body = MultiPoint(centroids).centroid
            for height, multipolygon in self._shapes3D.shapes.items():
                self._shapes3D.shapes[height] = affin.rotate(multipolygon, -90, origin=centroid_body, use_radians=False)
                self._shapes3D.shapes[height] = affin.translate(
                    self._shapes3D.shapes[height], xoff=-centroid_body.x, yoff=-centroid_body.y
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

    def _initialize_shapes2D(self, agent_type: cst.AgentTypes) -> Shapes2D:
        """
        Initialize 2D shapes for an agent depending on its type.

        Parameters
        ----------
        agent_type : AgentTypes
            The type of the agent (e.g., pedestrian, bike).

        Returns
        -------
        Shapes2D
            A `Shapes2D` object initialized with the provided input or default shapes.
        """
        shapes2D = Shapes2D(agent_type=agent_type)
        if agent_type == cst.AgentTypes.pedestrian:
            shapes2D.create_pedestrian_shapes(self._measures)
        elif agent_type == cst.AgentTypes.bike:
            shapes2D.create_bike_shapes(self._measures)
        return shapes2D

    def _initialize_shapes3D(self, agent_type: cst.AgentTypes) -> Shapes3D:
        """
        Initialize the 3D shapes for the agent.

        Parameters
        ----------
        agent_type : AgentTypes
            The type of the agent (e.g., pedestrian, bike).

        Returns
        -------
        Shapes3D
            Initialized 3D shapes for the agent.
        """
        shapes3D = Shapes3D(agent_type=agent_type)
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
            wanted_position = self.get_position()
            wanted_orientation = self.get_agent_orientation()

            # Create and update the 2D shapes
            self.shapes2D.create_pedestrian_shapes(self._measures)
            current_position = self.get_position()
            current_orientation = self.get_agent_orientation()
            self.translate(wanted_position.x - current_position.x, wanted_position.y - current_position.y)
            self.rotate(wanted_orientation - current_orientation)

            # Create and update the 3D shapes if they exist
            if self.shapes3D is not None:
                self.shapes3D.create_pedestrian3D(self._measures)
            else:
                self.shapes3D = Shapes3D(agent_type=cst.AgentTypes.pedestrian)
            self.shapes3D.create_pedestrian3D(self._measures)
            current_position = self.get_centroid_body3D()
            self.translate_body3D(dx=wanted_position.x - current_position.x, dy=wanted_position.y - current_position.y, dz=0.0)
            self.rotate_body3D(angle=wanted_orientation - 90)

        if self.agent_type == cst.AgentTypes.bike:
            if isinstance(value, dict):
                value = AgentMeasures(agent_type=cst.AgentTypes.bike, measures=value)
            self._measures = value
            wanted_position = self.get_position()
            wanted_orientation = self.get_agent_orientation()
            # Create and update the 2D shapes
            self.shapes2D.create_bike_shapes(self._measures)
            current_position = self.get_position()
            current_orientation = self.get_agent_orientation()
            self.translate(wanted_position.x - current_position.x, wanted_position.y - current_position.y)
            self.rotate(wanted_orientation - current_orientation)

        self._measures.measures[cst.CommonMeasures.moment_of_inertia.name] = fun.compute_moment_of_inertia(
            self._shapes2D.get_geometric_shape(),
            self._measures.measures[cst.CommonMeasures.weight.name],
        )

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
        rotated_body3D: dict[float, MultiPolygon] = {}
        centroid_body = self.get_centroid_body3D()
        # check if self.shapes3D is shapes3D object
        if self.shapes3D is None:
            raise ValueError("No 3D shapes available for the agent.")
        if not isinstance(self.shapes3D, Shapes3D):
            raise ValueError("shapes3D should be an instance of Shapes3D.")
        if not self.shapes3D.shapes:
            raise ValueError("No 3D shapes available for rotation.")
        for height, multipolygon in self.shapes3D.shapes.items():
            rotated_body3D[height] = affin.rotate(multipolygon, angle, origin=centroid_body, use_radians=False)
        self.shapes3D.shapes = rotated_body3D

    def get_centroid_body3D(self) -> MultiPoint:
        """
        Calculate the centroid of the agent's 3D body.

        Returns
        -------
        MultiPoint
            The centroid of the agent's 3D body, calculated as the centroid of
            all 3D shapes.

        Raises
        ------
        ValueError
            If shapes3D is None or contains no 3D shapes.
        """
        centroid_body = []
        if self.shapes3D is None:
            raise ValueError("No 3D shapes available for the agent.")
        for multipolygon in self.shapes3D.shapes.values():
            if isinstance(multipolygon, (MultiPolygon, Polygon)):
                centroid_body.append(multipolygon.centroid)
        centroid_body = MultiPoint(centroid_body).centroid
        return centroid_body

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
        if self.agent_type != cst.AgentTypes.pedestrian:
            raise ValueError("It does not make sense to use the 'get_delta_GtoGi' function for agents other than pedestrians.")
        delta_GtoGi = {}
        agent_center: Point = self.get_position()
        for name, shape in self.shapes2D.shapes.items():
            shape_center_x: float = shape["object"].centroid.x
            shape_center_y: float = shape["object"].centroid.y
            delta_GtoGi[name] = (shape_center_x - agent_center.x, shape_center_y - agent_center.y)
        return delta_GtoGi

    def get_agent_orientation(self) -> float:
        """
        Get the agent's orientation angle as the direction orthogonal to the one given by the shoulders.

        The shoulders direction is computed from the first shape minus the last shape position.

        Returns
        -------
        float
            The angle of the agent in degrees.
        """
        if self.agent_type == cst.AgentTypes.pedestrian:
            delta_GtoGi: dict[str, tuple[float, float]] = self.get_delta_GtoGi()
            delta_GtoG0: NDArray[np.float64] = np.array(delta_GtoGi["disk0"])
            delta_GtoG4: NDArray[np.float64] = np.array(delta_GtoGi["disk4"])
            shoulders_direction: NDArray[np.float64] = (delta_GtoG0 - delta_GtoG4) / np.linalg.norm(delta_GtoG0 - delta_GtoG4)
            head_orientation: float = np.arctan2(shoulders_direction[1], shoulders_direction[0]) - np.pi / 2
            head_orientation_degrees: float = fun.wrap_angle(np.degrees(head_orientation))
            return head_orientation_degrees
        if self.agent_type == cst.AgentTypes.bike:
            # the direction is given by the bike (not the rider)
            head_orientation_degrees = fun.direction_of_longest_side(self.shapes2D.shapes["bike"]["object"])
            return head_orientation_degrees
        raise ValueError("Agent type not supported for orientation calculation.")
