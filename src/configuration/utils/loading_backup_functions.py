"""Contains functions to save to xml, json, and pickle formats and also to load from them."""

import pickle
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from xml.dom import minidom

import pandas as pd

from configuration.utils.typing_custom import (
    DynamicCrowdDataType,
    GeometryDataType,
    IntrinsicMaterialDataType,
    MaterialsDataType,
    PairMaterialsDataType,
    ShapeDataType,
    StaticCrowdDataType,
)


def load_pickle(file_path: Path) -> Any:
    """
    Load data from a pickle file.

    This function deserializes and loads data from a specified pickle file.
    Pickle files are commonly used to store Python objects in a serialized format.

    Parameters
    ----------
    file_path : Path
        A `Path` object representing the path to the pickle file to be loaded.

    Returns
    -------
    Any
        The deserialized data loaded from the pickle file. The type of the
        returned object depends on what was serialized into the pickle file.
    """
    with open(file_path, "rb") as f:
        data = pickle.load(f)
    return data


def save_pickle(data: Any, file_path: Path) -> None:
    """
    Save data to a pickle file.

    This function serializes the given data and saves it to a specified file
    in pickle format. Pickle files are commonly used to store Python objects
    in a serialized format for later use.

    Parameters
    ----------
    data : Any
        The data to be serialized and saved. This can be any Python object
        that is supported by the `pickle` module.
    file_path : Path
        A `Path` object representing the path where the pickle file will be saved.

    Raises
    ------
    IOError
        If there is an issue opening or writing to the file.
    pickle.PicklingError
        If the object cannot be pickled (e.g., unsupported data types).
    """
    with open(file_path, "wb") as f:
        pickle.dump(data, f)


def load_csv(filename: Path) -> pd.DataFrame:
    """
    Load data from a CSV file into a pandas DataFrame.

    Parameters
    ----------
    filename : Path
        A `Path` object representing the path to the CSV file to be loaded.

    Returns
    -------
    pd.DataFrame
        A pandas DataFrame containing the data from the CSV file.
    """
    return pd.read_csv(filename)


def static_parameters_pedestrians_dict_to_xml(crowd_dict: StaticCrowdDataType) -> bytes:
    """
    Convert a dictionary containing static parameters of agents into an XML representation.

    Parameters
    ----------
    crowd_dict : StaticCrowdDataType
        A dictionary containing agent data.

    Returns
    -------
    bytes
        A prettified XML string in UTF-8 encoding representing the agents and their parameters.
    """
    # Create the root element <Agents>
    root = ET.Element("Agents")

    # Iterate through each agent in the dictionary
    for agent_data in crowd_dict["Agents"].values():
        # Create an <Agent> element with attributes
        agent = ET.SubElement(
            root,
            "Agent",
            {
                "type": agent_data["type"],
                "id": str(agent_data["id"]),
                "mass": str(agent_data["mass"]),
                "moi": str(agent_data["moi"]),
                "FloorDamping": str(agent_data["FloorDamping"]),
                "AngularDamping": str(agent_data["AngularDamping"]),
            },
        )

        # Create a <Shapes> element under the current <Agent>
        shapes = ET.SubElement(agent, "Shapes")

        # Iterate through each shape in the agent's shapes
        for shape_data in agent_data["Shapes"].values():
            shape_type = shape_data["type"]
            if shape_type == "circle":
                shape_type = "disk"
            # Create a <Shape> element with attributes
            ET.SubElement(
                shapes,
                "Shape",
                {
                    "type": shape_type,
                    "radius": str(shape_data["radius"]),
                    "material": str(shape_data["material"]),
                    "x": str(shape_data["x"]),
                    "y": str(shape_data["y"]),
                },
            )

    rough_string = ET.tostring(root, encoding="utf-8")
    reparsed = minidom.parseString(rough_string).toprettyxml(indent="    ", encoding="utf-8")

    return reparsed


def dynamic_parameters_dict_to_xml(dynamical_parameters_crowd: DynamicCrowdDataType) -> bytes:
    """
    Convert a dictionary containing dynamic parameters of agents into an XML representation.

    Parameters
    ----------
    dynamical_parameters_crowd : DynamicCrowdDataType
        A dictionary containing agent data.

    Returns
    -------
    bytes
        A prettified XML string in UTF-8 encoding representing the agents and their parameters.
    """
    # Create the root element
    root = ET.Element("Agents")

    # Iterate through agents in the dictionary
    for agent_data in dynamical_parameters_crowd["Agents"].values():
        # Create an Agent element
        agent_element = ET.SubElement(root, "Agent", id=str(agent_data["id"]))

        # Create Kinematics element
        kinematics_data = agent_data["Kinematics"]
        ET.SubElement(
            agent_element,
            "Kinematics",
            x=f"{kinematics_data['x']}",
            y=f"{kinematics_data['y']}",
            vx=f"{kinematics_data['vx']}",
            vy=f"{kinematics_data['vy']}",
            theta=f"{kinematics_data['theta']}",
            omega=f"{kinematics_data['omega']}",
        )

        # Create Dynamics element
        dynamics_data = agent_data["Dynamics"]
        ET.SubElement(
            agent_element,
            "Dynamics",
            Fpx=f"{dynamics_data['Fpx']}",
            Fpy=f"{dynamics_data['Fpy']}",
            Mp=f"{dynamics_data['Mp']}",
        )

    # Convert the tree to a string
    xml_str = ET.tostring(root, encoding="utf-8")

    # Prettify the XML string
    pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent="    ", encoding="utf-8")

    return pretty_xml_str


def geometry_dict_to_xml(boundaries_dict: GeometryDataType) -> bytes:
    """
    Save the given boundaries_dict dictionary to an XML file with UTF-8 encoding.

    Parameters
    ----------
    boundaries_dict : GeometryDataType
        A dictionary containing geometry data.

    Returns
    -------
    bytes
        A prettified XML string in UTF-8 encoding representing the geometry.
    """
    # Create the root element
    root = ET.Element("Geometry")

    # Add Dimensions element
    dimensions = boundaries_dict["Geometry"]["Dimensions"]
    ET.SubElement(root, "Dimensions", Lx=f"{dimensions['Lx']}", Ly=f"{dimensions['Ly']}")

    # Iterate over all walls in the dictionary
    for wall_data in boundaries_dict["Geometry"]["Wall"].values():
        # Add Wall element
        wall_element = ET.SubElement(root, "Wall", id=str(wall_data["id"]), material=f"{wall_data['material']}")

        # Add Corners element
        corners_element = ET.SubElement(wall_element, "Corners")
        for corner_data in wall_data["Corners"].values():
            ET.SubElement(corners_element, "Corner", x=f"{corner_data['x']}", y=f"{corner_data['y']}")

    # Convert the tree to a string
    xml_str = ET.tostring(root, encoding="utf-8")

    # Prettify the XML string
    pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent="    ", encoding="utf-8")

    return pretty_xml_str


def materials_dict_to_xml(material_dict: MaterialsDataType) -> bytes:
    """
    Save the given material_dict dictionary to an XML file with UTF-8 encoding.

    Parameters
    ----------
    material_dict : MaterialsDataType
        Dictionary containing material data.

    Returns
    -------
    bytes
        A prettified XML string in UTF-8 encoding representing the materials.
    """
    # Create the root element
    root = ET.Element("Materials")

    # Add Intrinsic materials
    intrinsic_element = ET.SubElement(root, "Intrinsic")
    for material_data in material_dict["Materials"]["Intrinsic"].values():
        ET.SubElement(
            intrinsic_element,
            "Material",
            id=str(material_data["id"]),
            name=material_data["name"],
            YoungModulus=f"{material_data['young_modulus']:.1f}",
            PoissonRatio=f"{material_data['poisson_ratio']:.1f}",
        )

    # Add Binary contacts
    binary_element = ET.SubElement(root, "Binary")
    for contact_data in material_dict["Materials"]["Binary"].values():
        ET.SubElement(
            binary_element,
            "Contact",
            id1=str(contact_data["id1"]),
            id2=str(contact_data["id2"]),
            GammaNormal=f"{contact_data['GammaNormal']:.3e}",
            GammaTangential=f"{contact_data['GammaTangential']:.3e}",
            KineticFriction=f"{contact_data['KineticFriction']:.5f}",
        )

    # Convert the tree to a string
    xml_str = ET.tostring(root, encoding="utf-8")

    # Prettify the XML string
    pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent="    ", encoding="utf-8")

    return pretty_xml_str


def static_parameters_pedestrians_xml_to_dict(xml_file: str) -> StaticCrowdDataType:
    """
    Convert an XML file to a Python dictionary.

    Parameters
    ----------
    xml_file : str
        Path to the XML file to be converted.

    Returns
    -------
    StaticCrowdDataType
        A dictionary representation of the XML file with the same format as the input dictionary.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Initialize the main dictionary structure
    crowd_dict: StaticCrowdDataType = {"Agents": {}}

    # Iterate over each <Agent> element in the XML
    for agent in root.findall("Agent"):
        agent_data: dict[str, int | float | ShapeDataType] = {
            "type": agent.get("type"),
            "id": int(agent.get("id", default=0)),
            "mass": float(agent.get("mass", default=0.0)),
            "moi": float(agent.get("moi", default=0.0)),
            "FloorDamping": float(agent.get("FloorDamping", default=0.0)),
            "AngularDamping": float(agent.get("AngularDamping", default=0.0)),
        }

        # Find <Shapes> element and process each <Shape> inside it
        shapes = agent.find("Shapes")
        if shapes is not None:
            shapes_dict: ShapeDataType = {}
            for i, shape in enumerate(shapes.findall("Shape"), start=1):
                shape_type = shape.get("type", default="circle")
                if shape_type == "disk":
                    shape_type = "circle"
                shape_data = {
                    "type": shape_type,
                    "radius": float(shape.get("radius", default=0.0)),
                    "material": shape.get("material", default="human"),
                    "x": float(shape.get("x", default=0.0)),
                    "y": float(shape.get("y", default=0.0)),
                }
                # Assign a unique name to each shape (e.g., disk1, disk2)
                shape_name = f"disk{i}"
                shapes_dict[shape_name] = shape_data
            agent_data["Shapes"] = shapes_dict

        # Assign a unique name to each agent (e.g., Agent0, Agent1)
        agent_name = f"Agent{len(crowd_dict['Agents'])}"
        crowd_dict["Agents"][agent_name] = agent_data

    return crowd_dict


def dynamic_parameters_xml_to_dict(xml_data: str) -> DynamicCrowdDataType:
    """
    Convert an XML string representing dynamic parameters of agents into a dictionary.

    Parameters
    ----------
    xml_data : str
        A string containing XML data.

    Returns
    -------
    DynamicCrowdDataType
        A dictionary representation of the XML data.
    """
    # Parse the XML data
    root = ET.fromstring(xml_data)

    # Extract agents and their kinematics and dynamics
    agents: DynamicCrowdDataType = {}

    for agent in root.findall("Agent"):
        agent_id = int(agent.get("id", default=0))

        # Extract kinematics
        kinematics = agent.find("Kinematics")
        if kinematics is None:
            raise ValueError("Kinematics data not found for agent.")
        kinematics_dict = {
            "x": float(kinematics.get("x", default=0.0)),
            "y": float(kinematics.get("y", default=0.0)),
            "vx": float(kinematics.get("vx", default=0.0)),
            "vy": float(kinematics.get("vy", default=0.0)),
            "theta": float(kinematics.get("theta", default=0.0)),
            "omega": float(kinematics.get("omega", default=0.0)),
        }

        # Extract dynamics
        dynamics = agent.find("Dynamics")
        if dynamics is None:
            raise ValueError("Dynamics data not found for agent.")
        dynamics_dict = {
            "Fpx": float(dynamics.get("Fpx", default=0.0)),
            "Fpy": float(dynamics.get("Fpy", default=0.0)),
            "Mp": float(dynamics.get("Mp", default=0.0)),
        }

        # Combine into agent dictionary
        agents[f"Agent{agent_id}"] = {
            "id": agent_id,
            "Kinematics": kinematics_dict,
            "Dynamics": dynamics_dict,
        }

    # Construct the final dictionary
    dynamical_parameters_crowd = {"Agents": agents}

    return dynamical_parameters_crowd


def geometry_xml_to_dict(xml_data: str) -> GeometryDataType:
    """
    Convert an XML string representing geometric data into a dictionary.

    Parameters
    ----------
    xml_data : str
        A string containing XML data.

    Returns
    -------
    GeometryDataType
        A dictionary representation of the XML data.
    """
    # Parse the XML data
    root = ET.fromstring(xml_data)

    # Extract dimensions
    dimensions = root.find("Dimensions")
    if dimensions is None:
        raise ValueError("Dimensions data not found in XML.")
    dimensions_dict = {"Lx": float(dimensions.get("Lx", default=0.0)), "Ly": float(dimensions.get("Ly", default=0.0))}

    # Extract walls and their corners
    walls: GeometryDataType = {}

    for wall in root.findall("Wall"):
        wall_id = int(wall.get("id", default=0))
        material = wall.get("material")

        corners: dict[str, dict[str, float]] = {}
        corners_element = wall.find("Corners")
        if corners_element is None:
            raise ValueError("Corners data not found for wall.")
        for i, corner in enumerate(corners_element.findall("Corner")):
            corners[f"Corner{i}"] = {"x": float(corner.get("x", default=0.0)), "y": float(corner.get("y", default=0.0))}

        walls[f"Wall{wall_id}"] = {
            "id": wall_id,
            "material": material,
            "Corners": corners,
        }

    # Construct the final dictionary
    boundaries_dict = {"Geometry": {"Dimensions": dimensions_dict, "Wall": walls}}

    return boundaries_dict


def materials_xml_to_dict(xml_data: str) -> MaterialsDataType:
    """
    Convert an XML string representing material properties into a dictionary.

    Parameters
    ----------
    xml_data : str
        A string containing XML data.

    Returns
    -------
    MaterialsDataType
        A dictionary representation of the XML data.
    """
    # Parse the XML data
    root = ET.fromstring(xml_data)

    # Extract intrinsic materials
    intrinsic_element = root.find("Intrinsic")
    if intrinsic_element is None:
        raise ValueError("Intrinsic materials data not found in XML.")

    intrinsic_materials: IntrinsicMaterialDataType = [
        {
            "id": int(material.get("id", default=0)),
            "name": material.get("name", default="iron"),
            "young_modulus": float(material.get("YoungModulus", default=0.0)),
            "poisson_ratio": float(material.get("PoissonRatio", default=0.0)),
        }
        for material in intrinsic_element
    ]

    # Extract binary contacts

    binary_element = root.find("Binary")
    if binary_element is None:
        raise ValueError("Binary contacts data not found in XML.")

    binary_contacts: PairMaterialsDataType = [
        {
            "id1": int(contact.get("id1", default=0)),
            "id2": int(contact.get("id2", default=1)),
            "GammaNormal": float(contact.get("GammaNormal", default=0.0)),
            "GammaTangential": float(contact.get("GammaTangential", default=0.0)),
            "KineticFriction": float(contact.get("KineticFriction", default=0.0)),
        }
        for contact in binary_element
    ]

    # Transform the data into the specified dictionary format
    material_dict: MaterialsDataType = {
        "Materials": {
            "Intrinsic": {f"Material{material['id']}": material for material in intrinsic_materials},
            "Binary": {f"Contact{i}": contact for i, contact in enumerate(binary_contacts)},
        }
    }

    return material_dict
