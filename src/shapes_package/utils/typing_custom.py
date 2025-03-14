"""Custom type definitions."""

from typing import Literal, TypeAlias

from shapely.geometry import MultiPolygon, Polygon

Sex: TypeAlias = Literal["male", "female"]
AgentType: TypeAlias = Literal["pedestrian", "bike", "custom"]
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
ShapeType: TypeAlias = Literal["circle", "rectangle", "ellipse", "polygon"]
BackupDataType: TypeAlias = Literal["json", "pickle", "xml"]
ShapeDataType: TypeAlias = (
    dict[str, dict[str, ShapeType | float | tuple[float, float]]]
    | dict[str, dict[str, ShapeType | float | Polygon | MultiPolygon]]
)
