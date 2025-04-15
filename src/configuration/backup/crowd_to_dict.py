"""Contains functions to save the crowd data in dictionary format."""

import itertools
from collections import defaultdict
from typing import Any, Dict

import numpy as np
from shapely.geometry import Point, Polygon

import configuration.utils.constants as cst
import configuration.utils.functions as fun
from configuration.models.crowd import Crowd
from configuration.utils.typing_custom import (
    DynamicCrowdDataType,
    GeometryDataType,
    IntrinsicMaterialDataType,
    MaterialsDataType,
    PairMaterialsDataType,
    ShapeType,
    StaticCrowdDataType,
)


def get_light_agents_params(current_crowd: Crowd) -> StaticCrowdDataType:
    """
    Retrieve the physical and geometric parameters of all agents in a structured format.

    Parameters
    ----------
    current_crowd : Crowd
        The current crowd object containing agent data.

    Returns
    -------
    CrowdDataType
        A dictionary containing agent data for all agents in the crowd.
    """
    crowd_dict: StaticCrowdDataType = {
        "Agents": {
            f"Agent{id_agent}": {
                "Type": f"{agent.agent_type.name}",
                "Id": id_agent,
                "Mass": agent.measures.measures[cst.CommonMeasures.weight.name],  # in kg
                "MomentOfInertia": agent.measures.measures["moment_of_inertia"],  # in kg*m^2
                "FloorDamping": cst.DEFAULT_FLOOR_DAMPING,
                "AngularDamping": cst.DEFAULT_ANGULAR_DAMPING,
                "Shapes": agent.shapes2D.get_additional_parameters(),
            }
            for id_agent, agent in enumerate(current_crowd.agents)
        }
    }

    return crowd_dict


def get_static_params(current_crowd: Crowd) -> StaticCrowdDataType:
    """
    Retrieve the physical and geometric parameters of all agents in a structured format.

    Parameters
    ----------
    current_crowd : Crowd
        The current crowd object containing agent data.

    Returns
    -------
    StaticCrowdDataType
        Static parameters of all agents in a nested dictionary format.
    """
    crowd_dict: StaticCrowdDataType = {"Agents": defaultdict(dict)}

    for agent_id, agent in enumerate(current_crowd.agents):
        # Initialize shapes dictionary for the current agent
        shapes_dict: dict[str, int | ShapeType | float | tuple[float, float]] = defaultdict(dict)
        all_shape_params = agent.shapes2D.get_additional_parameters()
        delta_g_to_gi: dict[str, tuple[float, float]] = agent.get_delta_GtoGi()
        theta: float = agent.get_agent_orientation()
        delta_g_to_gi_rotated = fun.rotate_vectors(delta_g_to_gi, -theta)

        # Extract all shape parameters for the current agent
        cpt_shape: int = 0
        for shape_name, shape_params in all_shape_params.items():
            delta_g_to_gi_shape = delta_g_to_gi_rotated[shape_name]

            # Add shape information to shapes_dict
            shapes_dict[f"{shape_name}"] = {
                "Id": cpt_shape,
                "Type": shape_params["type"],
                "Radius": shape_params["radius"],
                "MaterialId": getattr(cst.MaterialNames, shape_params["material"]).value - 1,
                "Position": (float(delta_g_to_gi_shape[0] * cst.CM_TO_M), float(delta_g_to_gi_shape[1] * cst.CM_TO_M)),
            }
            cpt_shape += 1

        # Add agent data to crowd_dict
        crowd_dict["Agents"][f"Agent{agent_id}"] = {
            "Type": agent.agent_type.name,
            "Id": agent_id,
            "Mass": agent.measures.measures[cst.CommonMeasures.weight.name],  # in kg
            "MomentOfInertia": float(agent.measures.measures["moment_of_inertia"]),  # in kg*m^2
            "FloorDamping": cst.DEFAULT_FLOOR_DAMPING,
            "AngularDamping": cst.DEFAULT_ANGULAR_DAMPING,
            "Shapes": shapes_dict,
        }

    return crowd_dict


def get_dynamic_params(current_crowd: Crowd) -> DynamicCrowdDataType:
    """
    Retrieve the physical and geometric parameters of all agents in a structured format.

    Parameters
    ----------
    current_crowd : Crowd
        The current crowd object containing agent data.

    Returns
    -------
    DynamicCrowdDataType
        Dynamical parameters of all agents.
    """
    dynamical_parameters_crowd: DynamicCrowdDataType = {
        "Agents": {
            f"Agent{id_agent}": {
                "Id": id_agent,
                "Kinematics": {
                    "Position": (agent.get_position().x * cst.CM_TO_M, agent.get_position().y * cst.CM_TO_M),
                    "Velocity": (cst.INITIAL_TRANSLATIONAL_VELOCITY_X, cst.INITIAL_TRANSLATIONAL_VELOCITY_Y),
                    "theta": np.radians(agent.get_agent_orientation()),
                    "omega": cst.INITIAL_ROTATIONAL_VELOCITY,
                },
                "Dynamics": {
                    "Fp": (cst.DECISIONAL_TRANSLATIONAL_FORCE_X, cst.DECISIONAL_TRANSLATIONAL_FORCE_Y),
                    "Mp": cst.DECISIONAL_TORQUE,
                },
            }
            for id_agent, agent in enumerate(current_crowd.agents)
        }
    }

    return dynamical_parameters_crowd


def get_geometry_params(current_crowd: Crowd) -> GeometryDataType:
    """
    Retrieve the parameters of the boundaries.

    Parameters
    ----------
    current_crowd : Crowd
        The current crowd object containing agent data.

    Returns
    -------
    GeometryDataType
        A dictionary containing the geometric parameters of the boundaries,
        including dimensions (Lx and Ly) and wall corner data.
    """
    # Ensure current_crowd.boundaries is a Polygon
    if not isinstance(current_crowd.boundaries, Polygon):
        raise ValueError("current_crowd.boundaries must be a shapely Polygon object.")
    current_boundaries = current_crowd.boundaries
    if current_boundaries.is_empty:
        # create a boundaries with a large square
        current_boundaries = Polygon(
            [
                Point(-cst.INFINITE, -cst.INFINITE),
                Point(-cst.INFINITE, cst.INFINITE),
                Point(cst.INFINITE, cst.INFINITE),
                Point(cst.INFINITE, -cst.INFINITE),
            ]
        )
    # Extract coordinates from the polygon's exterior
    coords = list(current_boundaries.exterior.coords)

    # Calculate Lx and Ly as maximum distances between x and y coordinates
    x_coords = [point[0] for point in coords]
    y_coords = [point[1] for point in coords]
    Lx = max(x_coords) - min(x_coords)
    Ly = max(y_coords) - min(y_coords)

    # Construct boundaries dictionary
    boundaries_dict: GeometryDataType = {
        "Geometry": {
            "Dimensions": {
                "Lx": Lx * cst.CM_TO_M,
                "Ly": Ly * cst.CM_TO_M,
            },
            "Wall": {
                "Wall0": {
                    "Id": 0,
                    "MaterialId": cst.MaterialNames.stone.value - 1,
                    "Corners": {
                        f"Corner{id_corner}": {
                            "Coordinates": (coords[id_corner][0] * cst.CM_TO_M, coords[id_corner][1] * cst.CM_TO_M),
                        }
                        for id_corner in range(len(coords))
                    },
                }
            },
        }
    }

    return boundaries_dict


def get_interactions_params(current_crowd: Crowd) -> Dict[str, Any]:
    """
    Retrieve the parameters for agent interactions.

    Parameters
    ----------
    current_crowd : Crowd
        The current crowd object containing agent data.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the parameters for agent interactions, structured to be saved as XML.
    """
    interactions_dict: Dict[str, Dict[str, Any]] = {"Interactions": {}}

    # Loop through all agents
    for id_agent1, agent1 in enumerate(current_crowd.agents):
        agent1_data: Dict[str, Any] = {
            "Id": id_agent1,
            "NeighbouringAgents": {},  # Initialize as an empty dictionary
        }
        shapes_agent1 = agent1.shapes2D.get_geometric_shapes()

        for id_agent2, agent2 in enumerate(current_crowd.agents):
            if id_agent1 == id_agent2:
                continue  # Skip self-interactions

            shapes_agent2 = agent2.shapes2D.get_geometric_shapes()
            interactions: Dict[str, Dict[str, int | float]] = {
                f"Interaction_{p_id}_{c_id}": {
                    "ParentShapeId": p_id,
                    "ChildShapeId": c_id,
                    "Ftx": cst.INITIAL_TANGENTIAL_FORCE_X,
                    "Fty": cst.INITIAL_TANGENTIAL_FORCE_Y,
                    "Fnx": cst.INITIAL_NORMAL_FORCE_X,
                    "Fny": cst.INITIAL_NORMAL_FORCE_Y,
                    "TangentialRelativeDisplacementNorm": cst.INITIAL_TANGENTIAL_RELATIVE_DISPLACEMENT_NORM,
                }
                for p_id, shape1 in enumerate(shapes_agent1)
                for c_id, shape2 in enumerate(shapes_agent2)
                if p_id <= c_id and shape1.intersects(shape2)
            }

            if interactions:  # Only add if there are interactions
                agent1_data["NeighbouringAgents"][f"Agent{id_agent2}"] = {
                    "Id": id_agent2,
                    "Interactions": interactions,
                }

        interactions_dict["Interactions"][f"Agent{id_agent1}"] = agent1_data

    return interactions_dict


# def get_interactions_params(current_crowd: Crowd) -> InteractionsDataType:
#     """
#     Retrieve the parameters for agent interactions.

#     Parameters
#     ----------
#     current_crowd : Crowd
#         The current crowd object containing agent data.

#     Returns
#     -------
#     InteractionsDataType
#         A dictionary containing the parameters for agent interactions, structured to be saved as XML.
#     """
#     interactions_dict: InteractionsDataType = {"Interactions": defaultdict(dict)}

#     # Loop through all agents
#     for id_agent1, agent1 in enumerate(current_crowd.agents):
#         agent1_data: dict[str, int | dict[str, int | dict[str, dict[str, int | float]]]] = {
#             "Id": id_agent1,
#             "NeighbouringAgents": defaultdict(dict),
#         }
#         shapes_agent1: list[Polygon] = agent1.shapes2D.get_geometric_shapes()

#         for id_agent2, agent2 in enumerate(current_crowd.agents):
#             if id_agent1 == id_agent2:
#                 continue  # Skip self-interactions

#             shapes_agent2: list[Polygon] = agent2.shapes2D.get_geometric_shapes()
#             interactions: dict[str, dict[str, int | float]] = {
#                 f"Interaction_{p_id}_{c_id}": {
#                     "ParentShapeId": p_id,
#                     "ChildShapeId": c_id,
#                     "Ftx": cst.INITIAL_TANGENTIAL_FORCE_X,
#                     "Fty": cst.INITIAL_TANGENTIAL_FORCE_Y,
#                     "Fnx": cst.INITIAL_NORMAL_FORCE_X,
#                     "Fny": cst.INITIAL_NORMAL_FORCE_Y,
#                     "TangentialRelativeDisplacementNorm": cst.INITIAL_TANGENTIAL_RELATIVE_DISPLACEMENT_NORM,
#                 }
#                 for p_id, shape1 in enumerate(shapes_agent1)
#                 for c_id, shape2 in enumerate(shapes_agent2)
#                 if p_id <= c_id and shape1.intersects(shape2)
#             }

#             if interactions:  # Only add if there are interactions
#                 agent1_data["NeighbouringAgents"][f"Agent{id_agent2}"] = {"Id": id_agent2, "Interactions": interactions}

#         interactions_dict["Interactions"][f"Agent{id_agent1}"] = agent1_data

#     return interactions_dict


def get_materials_params() -> MaterialsDataType:
    """
    Get the parameters of the materials.

    Returns
    -------
    MaterialsDataType
        A dictionary containing the parameters of the materials.
    """
    # Intrinsic material properties
    intrinsic_materials: IntrinsicMaterialDataType = {
        f"Material{id_material}": {
            "Id": id_material,
            "Name": material,
            "YoungModulus": getattr(cst, f"YOUNG_MODULUS_{material.upper()}"),
            "ShearModulus": getattr(cst, f"SHEAR_MODULUS_{material.upper()}"),
        }
        for id_material, material in enumerate(cst.MaterialNames.__members__.keys())
    }

    # Binary material properties (pairwise interactions)
    binary_materials: PairMaterialsDataType = {
        f"Contact{id_contact}": {
            "Id1": id1,
            "Id2": id2,
            "GammaNormal": cst.GAMMA_NORMAL,
            "GammaTangential": cst.GAMMA_TANGENTIAL,
            "KineticFriction": cst.KINETIC_FRICTION,
        }
        for id_contact, (id1, id2) in enumerate(itertools.combinations(range(len(cst.MaterialNames)), 2))
    }

    # Combine intrinsic and binary properties into a single dictionary
    materials_dict: MaterialsDataType = {
        "Materials": {
            "Intrinsic": intrinsic_materials,
            "Binary": binary_materials,
        }
    }

    return materials_dict
