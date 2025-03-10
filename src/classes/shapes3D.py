"""Class to store body shapes dynamically based on agent type."""

from dataclasses import dataclass, field
from typing import get_args

from shapely.affinity import scale
from shapely.geometry import MultiPoint, MultiPolygon

import src.utils.constants as cst
from src.classes.initial_agents import InitialPedestrian
from src.classes.measures import AgentMeasures
from src.utils.typing_custom import AgentType, SapeDataType


@dataclass
class Shapes3D:
    """
    Class to store body shapes dynamically based on agent type.
        either you provide a dictionary of shapely shapes as input
        or you specify the type of shape and its characteristics to create it dynamically.

    Attributes:
        agent_type (AgentType): The type of agent for which the shapes are being stored.
        shapes (SapeDataType): A dictionary where keys are heights (floats) and values are Shapely MultiPolygon objects.

    Methods:
        __post_init__() -> None:
        create_pedestrian3D(measurements: AgentMeasures) -> None:
    """

    agent_type: AgentType
    shapes: SapeDataType = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Validate the provided shapes and agent type after the object is initialized.

        Raises:
            ValueError: If the agent type is not one of the allowed values.
            ValueError: If the shapes attribute is not a dictionary.
            ValueError: If any of the shapes are not valid Shapely MultiPolygon objects.
            ValueError: If any of the heights are not of type float.
        """

        # Validate the provided agent type
        if self.agent_type not in get_args(AgentType):
            allowed_values = ", ".join(get_args(AgentType))
            raise ValueError(f"Agent type should be one of: {allowed_values}.")

        # Validate the provided shapes
        if not isinstance(self.shapes, dict):
            raise ValueError("shapes should be a dictionary.")

        # Validate that the provided shapes are valid Shapely objects
        for height, multipolygon in self.shapes.items():
            if not isinstance(multipolygon, MultiPolygon):
                raise ValueError(f"Invalid shape type for '{height}': {type(multipolygon)}")
            if not isinstance(height, float):
                raise ValueError(f"Invalid height type for '{height}': {type(height)}")

    def create_pedestrian3D(self, measurements: AgentMeasures) -> None:
        """
        Creates a 3D representation of a pedestrian based on the provided measurements.

        Args:
            measurements (AgentMeasures): An object containing the measurements of the pedestrian.

        Returns:
            None
        """

        # Scale the initial pedestrian shapes to match the provided measurements
        initial_pedestrian = InitialPedestrian(measurements.measures[cst.PedestrianParts.sex.name])

        scale_factor_x = (
            measurements.measures[cst.PedestrianParts.bideltoid_breadth.name]
            / initial_pedestrian.measures[cst.PedestrianParts.bideltoid_breadth.name]
        )
        scale_factor_y = (
            measurements.measures[cst.PedestrianParts.chest_depth.name]
            / initial_pedestrian.measures[cst.PedestrianParts.chest_depth.name]
        )
        scale_factor_z = (
            measurements.measures[cst.PedestrianParts.height.name] / initial_pedestrian.measures[cst.PedestrianParts.height.name]
        )

        current_body3D = {}
        homothety_center = MultiPoint([multipolygon.centroid for multipolygon in initial_pedestrian.shapes3D.values()]).centroid
        for height, multipolygon in initial_pedestrian.shapes3D.items():
            scaled_multipolygon = scale(
                multipolygon,
                xfact=scale_factor_x,
                yfact=scale_factor_y,
                origin=homothety_center,
            )
            scaled_height = height * scale_factor_z
            current_body3D[scaled_height] = scaled_multipolygon

        self.shapes = current_body3D
