"""Class to store body shapes dynamically based on agent type."""

from dataclasses import dataclass, field

from shapely.affinity import scale
from shapely.geometry import MultiPoint, MultiPolygon

import configuration.utils.constants as cst
from configuration.models.initial_agents import InitialPedestrian
from configuration.models.measures import AgentMeasures
from configuration.utils.typing_custom import ShapeDataType


@dataclass
class Shapes3D:
    """Store and manage 3D body shapes for different agent types."""

    agent_type: cst.AgentTypes
    shapes: ShapeDataType = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Validate dataclass attributes after initialization.

        Raises
        ------
        ValueError
            If any of the following validation checks fail:
            - Agent type is not a member of `AgentTypes`
            - Shapes container is not a dictionary
            - Shape values are not Shapely MultiPolygon objects
            - Height keys cannot be converted to float values
        """
        # Validate the provided agent type
        if not isinstance(self.agent_type, cst.AgentTypes):
            raise ValueError(f"Agent type should be one of: {[member.name for member in cst.AgentTypes]}.")

        # Validate the provided shapes
        if not isinstance(self.shapes, dict):
            raise ValueError("shapes should be a dictionary.")

        # Validate that the provided shapes are valid Shapely objects
        for height, multipolygon in self.shapes.items():
            if not isinstance(multipolygon, MultiPolygon):
                raise ValueError(f"Invalid shape type for '{height}': {type(multipolygon)}")
            try:
                float(height)
            except ValueError:
                raise ValueError(f"Invalid height type for '{height}': {type(height)}") from None

    def create_pedestrian3D(self, measurements: AgentMeasures) -> None:
        """
        Create a 3D representation of a pedestrian based on provided measurements.

        Parameters
        ----------
        measurements : AgentMeasures
            An object containing the target measurements of the pedestrian,
            including sex, bideltoid breadth, chest depth, and height.

        Raises
        ------
        ValueError
            If the provided sex in "measurements" is not "male" or "female".

        Notes
        -----
        - The method uses an initial pedestrian representation based on the provided sex.
        - Scaling factors are calculated for each dimension (x, y, z) based on
          the ratio of target measurements to initial measurements.
        """
        # Extract sex from measurements and create initial pedestrian object
        sex_name = measurements.measures[cst.PedestrianParts.sex.name]
        if isinstance(sex_name, str) and sex_name in ["male", "female"]:
            initial_pedestrian = InitialPedestrian(sex_name)
        else:
            raise ValueError(f"Invalid sex name: {sex_name}. Expected 'male' or 'female'.")

        # Calculate scaling factors for each dimension
        scale_factor_x = float(measurements.measures[cst.PedestrianParts.bideltoid_breadth.name]) / float(
            initial_pedestrian.measures[cst.PedestrianParts.bideltoid_breadth.name]
        )
        scale_factor_y = float(measurements.measures[cst.PedestrianParts.chest_depth.name]) / float(
            initial_pedestrian.measures[cst.PedestrianParts.chest_depth.name]
        )
        scale_factor_z = float(measurements.measures[cst.PedestrianParts.height.name]) / float(
            initial_pedestrian.measures[cst.PedestrianParts.height.name]
        )

        # Initialize dictionary to store scaled 3D shapes
        current_body3D: ShapeDataType = {}

        # Calculate the center point for scaling (centroid of all initial shapes)
        homothety_center = MultiPoint([multipolygon.centroid for multipolygon in initial_pedestrian.shapes3D.values()]).centroid

        # Scale each component of the initial 3D representation
        for height, multipolygon in initial_pedestrian.shapes3D.items():
            scaled_multipolygon = scale(
                multipolygon,
                xfact=scale_factor_x,
                yfact=scale_factor_y,
                origin=homothety_center,
            )
            scaled_height = height * scale_factor_z
            current_body3D[scaled_height] = MultiPolygon(scaled_multipolygon)

        # Update the shapes attribute with the new 3D representation
        self.shapes = current_body3D
