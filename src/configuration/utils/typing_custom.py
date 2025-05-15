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
    "disk",
    "rectangle",
    "polygon",
]

#: Represents common materials used in crowd simulations.
MaterialType: TypeAlias = Literal[
    "concrete",
    "human_naked",
    "human_clothes",
]

#: Represents supported backup data formats.
BackupDataType: TypeAlias = Literal[
    "pickle",
    "xml",
]

#: Represents the structure of shape-related data.
ShapeDataType: TypeAlias = (
    dict[str, dict[str, ShapeType | MaterialType | float]]
    | dict[str, dict[str, ShapeType | MaterialType | float | Polygon | MultiPolygon]]
)

#: Represents the structure of acrowd-related data.
StaticCrowdDataType: TypeAlias = dict[str, dict[str, dict[str, AgentType | float | int | ShapeDataType]]]

#: Represents the structure of dynamic crowd-related data.
DynamicCrowdDataType: TypeAlias = dict[
    str,  # Top-level key ("Agents")
    dict[
        str,  # Keys inside "Agents" ("Agent0", "Agent1", ...)
        dict[
            str,  # Keys inside each agent ("id", "Kinematics", "Dynamics")
            int | dict[str, float],
        ],
    ],
]

#: Represents the structure of geometry-related data.
GeometryDataType: TypeAlias = dict[
    str,  # Top-level key ("Geometry")
    dict[
        str,  # Keys inside "Geometry" ("Dimensions", "Wall")
        dict[str, float]
        | dict[
            str,  # Keys inside "Wall" ("Wall0", "Wall1", ...)
            dict[str, int | MaterialType | dict[str, dict[str, float]]],
        ],
    ],
]

#: Represents the intrinsic properties of each material.
IntrinsicMaterialDataType = dict[str, dict[str, int | str | float]]

#: Represents the properties associated with each pair of material.
PairMaterialsDataType = dict[str, dict[str, int | float]]

#: Represents the structure of material-related data.
MaterialsDataType = dict[
    str,  # Top-level key ("Material")
    dict[
        str,  # Keys inside "Material" ("Intrinsic", "Binary")
        IntrinsicMaterialDataType | PairMaterialsDataType,
    ],
]

#: Represents the structure of interaction-related data.
InteractionsDataType: TypeAlias = dict[
    str,  # Top-level key ("Interactions")
    dict[
        str,  # Keys inside "Interactions" ("Agent0", "Agent1", ...)
        dict[
            str,  # Keys inside each agent ("Id", "NeighbouringAgents")
            int
            | dict[
                str,  # Keys inside "NeighbouringAgents" ("Id", "Interactions"
                int
                | dict[
                    str,  # Keys inside "Interactions" ("Interaction_0_0", "Interaction_0_1", ...)
                    dict[
                        str,  # Keys inside each interaction ("ParentShapeId", "ChildShapeId", "Ftx", ...)
                        int | tuple[float, float],
                    ],
                ],
            ],
        ],
    ],
]
