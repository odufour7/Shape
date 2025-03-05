from dataclasses import dataclass
from enum import Enum, auto
from typing import Literal, TypeAlias

import shapely

Sex: TypeAlias = Literal["male", "female"]
AgentType: TypeAlias = Literal["pedestrian", "bike"]


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
    __annotations__ = {part.name: float for part in PedestrianBodyParts or BikeParts or something else}

    def __post_init__(self):
        for part in PedestrianBodyParts or BikeParts or something else:
            if not hasattr(self, part.name):
                raise ValueError(f"Missing measure for {part.name}")


@dataclass
class BodyShapes:
    __annotations__ = {part.name: shapely.Geometry for part in PedestrianBodyParts}


def relative_position(geo1, geo2):
    return geo1.xy - geo2.xy


class Agent:
    def __init__(
        self,
        sex: Sex | None,
        agent_type: AgentType,
        measures: BodyMeasures | dict[str, float],
        shapes: BodyShapes | dict[str, shapely.Geometry],
        modulus: dict[str, float],
    ) -> None:
        if isinstance(measures, dict):
            measures = BodyMeasures(**measures)

        if isinstance(shapes, dict):
            shapes = BodyShapes(**shapes)

        self.sex = sex
        self.agent_type = agent_type
        self.measures = measures
        self.shapes = shapes
        self.modulus = modulus

    def rotate(self, angle: float) -> None: ...

    def translate(self, x: float, y: float) -> None: ...
