"""Contains functions to save to different formats including xml, zip and also to load from them."""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from xml.dom.minidom import parseString

from dicttoxml import dicttoxml

import configuration.utils.functions as fun
from configuration.utils.typing_custom import (
    DynamicCrowdDataType,
    GeometryDataType,
    InteractionsDataType,
    IntrinsicMaterialDataType,
    MaterialsDataType,
    PairMaterialsDataType,
    ShapeDataType,
    StaticCrowdDataType,
)


def save_light_agents_params_dict_to_xml(crowd_data_dict: StaticCrowdDataType) -> str:
    """
    Generate a pretty-printed XML string of agent parameters from a Crowd object.

    Parameters
    ----------
    crowd_data_dict : StaticCrowdDataType
        A dictionary containing agent data for all agents in the crowd.

    Returns
    -------
    str
        A string representation of the XML data.
    """
    # Convert dictionary to XML string without type attributes
    xml_data = dicttoxml(crowd_data_dict, attr_type=False, root=False)

    # Parse the XML string into a DOM object
    dom = parseString(xml_data)

    # Pretty-print the XML with indentation and remove empty lines
    pretty_xml = dom.toprettyxml(indent="     ")
    data = "\n".join([line for line in pretty_xml.split("\n") if line.strip()])

    return data


def static_dict_to_xml(crowd_dict: StaticCrowdDataType) -> bytes:
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
                "Type": agent_data["Type"],
                "Id": f"{agent_data['Id']}",
                "Mass": f"{agent_data['Mass']:.2f}",
                "MomentOfInertia": f"{agent_data['MomentOfInertia']:.2f}",
                "FloorDamping": f"{agent_data['FloorDamping']:.2f}",
                "AngularDamping": f"{agent_data['AngularDamping']:.2f}",
            },
        )

        # Create a <Shapes> element under the current <Agent>
        shapes = ET.SubElement(agent, "Shapes")

        # Iterate through each shape in the agent's shapes
        for shape_data in agent_data["Shapes"].values():
            shape_type = shape_data["Type"]

            # Create a <Shape> element with attributes
            ET.SubElement(
                shapes,
                "Shape",
                {
                    "Id": f"{shape_data['Id']}",
                    "Type": shape_type,
                    "Radius": f"{shape_data['Radius']:.3f}",
                    "MaterialId": f"{shape_data['MaterialId']}",
                    "Position": f"{shape_data['Position'][0]:.3f},{shape_data['Position'][1]:.3f}",
                },
            )

    rough_string = ET.tostring(root, encoding="utf-8")
    reparsed = minidom.parseString(rough_string).toprettyxml(indent="    ", encoding="utf-8")

    return reparsed


def dynamic_dict_to_xml(dynamical_parameters_crowd: DynamicCrowdDataType) -> bytes:
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
        agent_element = ET.SubElement(root, "Agent", Id=f"{agent_data['Id']}")

        # Create Kinematics element
        kinematics_data = agent_data["Kinematics"]
        ET.SubElement(
            agent_element,
            "Kinematics",
            Position=f"{kinematics_data['Position'][0]:.3f},{kinematics_data['Position'][1]:.3f}",
            Velocity=f"{kinematics_data['Velocity'][0]:.2f},{kinematics_data['Velocity'][1]:.2f}",
            theta=f"{kinematics_data['theta']:.2f}",
            omega=f"{kinematics_data['omega']:.2f}",
        )

        # Create Dynamics element
        dynamics_data = agent_data["Dynamics"]
        ET.SubElement(
            agent_element,
            "Dynamics",
            Fp=f"{dynamics_data['Fp'][0]:.2f},{dynamics_data['Fp'][1]:.2f}",
            Mp=f"{dynamics_data['Mp']:.2f}",
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
    ET.SubElement(root, "Dimensions", Lx=f"{dimensions['Lx']:.3f}", Ly=f"{dimensions['Ly']:.3f}")

    # Iterate over all walls in the dictionary
    for wall_data in boundaries_dict["Geometry"]["Wall"].values():
        # Add Wall element
        wall_element = ET.SubElement(root, "Wall", Id=f"{wall_data['Id']}", MaterialId=f"{wall_data['MaterialId']}")

        # Add Corners element
        corners_element = ET.SubElement(wall_element, "Corners")
        for corner_data in wall_data["Corners"].values():
            ET.SubElement(
                corners_element, "Corner", Coordinates=f"{corner_data['Coordinates'][0]:.3f},{corner_data['Coordinates'][1]:.3f}"
            )

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
            Id=f"{material_data['Id']}",
            Name=material_data["Name"],
            YoungModulus=f"{material_data['YoungModulus']:.2e}",
            ShearModulus=f"{material_data['ShearModulus']:.2e}",
        )

    # Add Binary contacts
    binary_element = ET.SubElement(root, "Binary")
    for contact_data in material_dict["Materials"]["Binary"].values():
        ET.SubElement(
            binary_element,
            "Contact",
            Id1=f"{contact_data['Id1']}",
            Id2=f"{contact_data['Id2']}",
            GammaNormal=f"{contact_data['GammaNormal']:.2e}",
            GammaTangential=f"{contact_data['GammaTangential']:.2e}",
            KineticFriction=f"{contact_data['KineticFriction']:.2f}",
        )

    # Convert the tree to a string
    xml_str = ET.tostring(root, encoding="utf-8")

    # Prettify the XML string
    pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent="    ", encoding="utf-8")

    return pretty_xml_str


def interactions_dict_to_xml(data: InteractionsDataType) -> bytes:
    """
    Save the given interactions dictionary to an XML file with UTF-8 encoding.

    Parameters
    ----------
    data : InteractionsDataType
        A dictionary containing interactions data.

    Returns
    -------
    bytes
        A prettified XML string in UTF-8 encoding representing the interactions.
    """
    # Create the root element
    root = ET.Element("Interactions")

    # Iterate through agents in the dictionary
    for agent_data in data["Interactions"].values():
        agent_element = ET.SubElement(root, "Agent", Id=f"{agent_data['Id']}")
        # Iterate through neighboring agents
        if "NeighbouringAgents" in agent_data:
            for neighbor_data in agent_data["NeighbouringAgents"].values():
                neighbor_element = ET.SubElement(agent_element, "Agent", Id=f"{neighbor_data['Id']}")

                # Iterate through interactions
                for interaction_data in neighbor_data["Interactions"].values():
                    ET.SubElement(
                        neighbor_element,
                        "Interaction",
                        ParentShapeId=f"{interaction_data['ParentShapeId']}",
                        ChildShapeId=f"{interaction_data['ChildShapeId']}",
                        Ftx=f"{interaction_data['Ftx']:.2f}",
                        Fty=f"{interaction_data['Fty']:.2f}",
                        Fnx=f"{interaction_data['Fnx']:.2f}",
                        Fny=f"{interaction_data['Fny']:.2f}",
                        TangentialRelativeDisplacementNorm=f"{interaction_data['TangentialRelativeDisplacementNorm']:.2f}",
                    )
    # Convert the tree to a string
    xml_str = ET.tostring(root, encoding="utf-8")

    # Prettify the XML string
    pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent="    ", encoding="utf-8")

    return pretty_xml_str


def static_xml_to_dict(xml_file: str) -> StaticCrowdDataType:
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
    # Parse the XML file
    root = ET.fromstring(xml_file)

    # Initialize the main dictionary structure
    crowd_dict: StaticCrowdDataType = {"Agents": {}}

    # Iterate over each <Agent> element in the XML
    for agent in root.findall("Agent"):
        agent_data: dict[str, int | float | ShapeDataType] = {
            "Type": agent.get("Type"),
            "Id": int(agent.get("Id", default=0)),
            "Mass": float(agent.get("Mass", default=0.0)),
            "MomentOfInertia": float(agent.get("MomentOfInertia", default=0.0)),
            "FloorDamping": float(agent.get("FloorDamping", default=0.0)),
            "AngularDamping": float(agent.get("AngularDamping", default=0.0)),
        }

        # Find <Shapes> element and process each <Shape> inside it
        shapes = agent.find("Shapes")
        if shapes is not None:
            shapes_dict: ShapeDataType = {}
            for i, shape in enumerate(shapes.findall("Shape"), start=0):
                shape_type = shape.get("Type", default="disk")
                shape_data = {
                    "Id": int(shape.get("Id", default=0)),
                    "Type": shape_type,
                    "Radius": float(shape.get("Radius", default=0.0)),
                    "MaterialId": int(shape.get("MaterialId", default=0)),
                    "Position": fun.from_string_to_tuple(shape.get("Position", default="0.0,0.0")),
                }
                # Assign a unique name to each shape (e.g., disk1, disk2)
                shape_name = f"disk{i}"
                shapes_dict[shape_name] = shape_data
            agent_data["Shapes"] = shapes_dict

        # Assign a unique name to each agent (e.g., Agent0, Agent1)
        agent_name = f"Agent{len(crowd_dict['Agents'])}"
        crowd_dict["Agents"][agent_name] = agent_data

    return crowd_dict


def dynamic_xml_to_dict(xml_data: str) -> DynamicCrowdDataType:
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
        agent_id = int(agent.get("Id", default=0))

        # Extract kinematics
        kinematics = agent.find("Kinematics")
        if kinematics is None:
            raise ValueError("Kinematics data not found for agent.")
        kinematics_dict = {
            "Position": fun.from_string_to_tuple(kinematics.get("Position", default="0.0,0.0")),
            "Velocity": fun.from_string_to_tuple(kinematics.get("Velocity", default="0.0,0.0")),
            "theta": float(kinematics.get("theta", default=0.0)),
            "omega": float(kinematics.get("omega", default=0.0)),
        }

        # Extract dynamics
        dynamics = agent.find("Dynamics")
        if dynamics is None:
            raise ValueError("Dynamics data not found for agent.")
        dynamics_dict = {
            "Fp": fun.from_string_to_tuple(dynamics.get("Fp", default="0.0,0.0")),
            "Mp": float(dynamics.get("Mp", default=0.0)),
        }

        # Combine into agent dictionary
        agents[f"Agent{agent_id}"] = {
            "Id": agent_id,
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
        wall_id = int(wall.get("Id", default=0))
        id_material = int(wall.get("MaterialId", 0))

        corners: dict[str, dict[str, float]] = {}
        corners_element = wall.find("Corners")
        if corners_element is None:
            raise ValueError("Corners data not found for wall.")
        for i, corner in enumerate(corners_element.findall("Corner")):
            corners[f"Corner{i}"] = {"Coordinates": fun.from_string_to_tuple(corner.get("Coordinates", default="0.0,0.0"))}

        walls[f"Wall{wall_id}"] = {
            "Id": wall_id,
            "MaterialId": id_material,
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
            "Id": int(material.get("Id", default=0)),
            "Name": material.get("Name", default="iron"),
            "YoungModulus": float(material.get("YoungModulus", default=0.0)),
            "ShearModulus": float(material.get("ShearModulus", default=0.0)),
        }
        for material in intrinsic_element
    ]

    # Extract binary contacts
    binary_element = root.find("Binary")
    if binary_element is None:
        raise ValueError("Binary contacts data not found in XML.")

    binary_contacts: PairMaterialsDataType = [
        {
            "Id1": int(contact.get("Id1", default=0)),
            "Id2": int(contact.get("Id2", default=1)),
            "GammaNormal": float(contact.get("GammaNormal", default=0.0)),
            "GammaTangential": float(contact.get("GammaTangential", default=0.0)),
            "KineticFriction": float(contact.get("KineticFriction", default=0.0)),
        }
        for contact in binary_element
    ]

    # Transform the data into the specified dictionary format
    material_dict: MaterialsDataType = {
        "Materials": {
            "Intrinsic": {f"Material{material['Id']}": material for material in intrinsic_materials},
            "Binary": {f"Contact{i}": contact for i, contact in enumerate(binary_contacts)},
        }
    }

    return material_dict


def interactions_xml_to_dict(xml_data: str) -> InteractionsDataType:
    """
    Convert an XML file describing interactions into a nested dictionary structure.

    Parameters
    ----------
    xml_data : str
        A string containing XML data.

    Returns
    -------
    InteractionsDataType
        A dictionary representation of the XML data.
    """
    root = ET.fromstring(xml_data)

    interactions_dict: InteractionsDataType = {"Interactions": {}}

    # Iterate through all Agent elements in the XML
    for agent in root.findall("Agent"):
        agent_id = int(agent.attrib["Id"])
        agent_key = f"Agent{agent_id}"
        interactions_dict["Interactions"][agent_key] = {"Id": agent_id, "NeighbouringAgents": {}}

        # Iterate through neighboring agents
        for neighbor_agent in agent.findall("Agent"):
            neighbor_id = int(neighbor_agent.attrib["Id"])
            neighbor_key = f"Agent{neighbor_id}"
            interactions_dict["Interactions"][agent_key]["NeighbouringAgents"][neighbor_key] = {"Id": neighbor_id, "Interactions": {}}

            # Iterate through interactions
            for interaction in neighbor_agent.findall("Interaction"):
                parent_shape_id = int(interaction.attrib["ParentShapeId"])
                child_shape_id = int(interaction.attrib["ChildShapeId"])
                interaction_key = f"Interaction_{parent_shape_id}_{child_shape_id}"

                # Add interaction details to the dictionary
                interactions_dict["Interactions"][agent_key]["NeighbouringAgents"][neighbor_key]["Interactions"][interaction_key] = {
                    "ParentShapeId": parent_shape_id,
                    "ChildShapeId": child_shape_id,
                    "Ftx": float(interaction.attrib["Ftx"]),
                    "Fty": float(interaction.attrib["Fty"]),
                    "Fnx": float(interaction.attrib["Fnx"]),
                    "Fny": float(interaction.attrib["Fny"]),
                    "TangentialRelativeDisplacementNorm": float(interaction.attrib["TangentialRelativeDisplacementNorm"]),
                }

    return interactions_dict
