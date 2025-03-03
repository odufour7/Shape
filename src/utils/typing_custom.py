""" Custom type definitions """

from typing import Literal, TypeAlias

from shapely.geometry import Polygon

Sex: TypeAlias = Literal["male", "female"]
AgentType: TypeAlias = Literal["pedestrian", "bike", "custom"]
ShapeType: TypeAlias = Literal["circle", "rectangle", "ellipse", "polygon"]
BackupDataType: TypeAlias = Literal["json", "pickle", "xml"]
SapeDataType: TypeAlias = (
    dict[str, dict[str, ShapeType | float | tuple[float, float]]] | dict[str, dict[str, ShapeType | float | Polygon]]
)
