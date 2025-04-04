"""Custom type definitions."""

from typing import Literal, TypeAlias

from shapely.geometry import MultiPolygon, Polygon

#: Represents biological sex categories.
Sex: TypeAlias = Literal[
    "male",
    "female",
]

#: Represents different types of agents in the system.
AgentType: TypeAlias = Literal[
    "pedestrian",
    "bike",
    "custom",
]

#: Represents the parts of an agent (e.g., physical dimensions).
AgentPart: TypeAlias = Literal[
    "chest_depth",
    "bideltoid_breadth",
    "height",
    "sex",
    "wheel_width",
    "total_length",
    "handlebar_length",
    "top_tube_length",
]

#: Represents different types of shapes used in geometry.
ShapeType: TypeAlias = Literal[
    "circle",
    "rectangle",
    "ellipse",
    "polygon",
]

#: Represents supported backup data formats.
BackupDataType: TypeAlias = Literal[
    "json",
    "pickle",
    "xml",
]

#: Represents the structure of shape-related data.
ShapeDataType: TypeAlias = (
    dict[str, dict[str, ShapeType | float | tuple[float, float]]]
    | dict[str, dict[str, ShapeType | float | Polygon | MultiPolygon]]
)
