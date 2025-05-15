"""Contains functions to save to different formats including xml, zip and also to load from them."""

import xml.etree.ElementTree as ET
from typing import Any
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
                "Height": f"{agent_data['Height']:.2f}",
                "MomentOfInertia": f"{agent_data['MomentOfInertia']:.2f}",
                "FloorDamping": f"{agent_data['FloorDamping']:.2f}",
                "AngularDamping": f"{agent_data['AngularDamping']:.2f}",
            },
        )

        # Iterate through each shape in the agent's shapes
        for shape_data in agent_data["Shapes"].values():
            # Create a <Shape> element with attributes
            ET.SubElement(
                agent,
                "Shape",
                {
                    "Type": shape_data["Type"],
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
        for corner_data in wall_data["Corners"].values():
            ET.SubElement(
                wall_element, "Corner", Coordinates=f"{corner_data['Coordinates'][0]:.3f},{corner_data['Coordinates'][1]:.3f}"
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
                        ParentShape=f"{interaction_data['ParentShape']}",
                        ChildShape=f"{interaction_data['ChildShape']}",
                        TangentialRelativeDisplacement=f"{interaction_data['TangentialRelativeDisplacement'][0]:.2f},{interaction_data['TangentialRelativeDisplacement'][1]:.2f}",
                        Fn=f"{interaction_data['Fn'][0]:.2f},{interaction_data['Fn'][1]:.2f}",
                        Ft=f"{interaction_data['Ft'][0]:.2f},{interaction_data['Ft'][1]:.2f}",
                    )
    # Convert the tree to a string
    xml_str = ET.tostring(root, encoding="utf-8")

    # Prettify the XML string
    pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent="    ", encoding="utf-8")

    return pretty_xml_str


def static_xml_to_dict(xml_file: str) -> StaticCrowdDataType:
    """
    Convert an XML string representing static agent data into a dictionary, with strict validation of structure and attribute types.

    Parameters
    ----------
    xml_file : str
        XML data as a string.

    Returns
    -------
    StaticCrowdDataType
        A dictionary representation of the XML data.

    Raises
    ------
    ValueError
        If the XML structure or attribute types are incorrect.
    """
    try:
        root = ET.fromstring(xml_file)
    except ET.ParseError as e:
        raise ValueError(f"Malformed XML: {e}") from e

    crowd_dict: StaticCrowdDataType = {"Agents": {}}

    for agent_idx, agent in enumerate(root.findall("Agent")):
        # Validate required agent attributes
        try:
            agent_data: dict[str, Any] = {
                "Type": agent.attrib["Type"],
                "Id": int(agent.attrib["Id"]),
                "Mass": float(agent.attrib["Mass"]),
                "Height": float(agent.attrib["Height"]),
                "MomentOfInertia": float(agent.attrib["MomentOfInertia"]),
                "FloorDamping": float(agent.attrib["FloorDamping"]),
                "AngularDamping": float(agent.attrib["AngularDamping"]),
            }
        except KeyError as e:
            raise ValueError(f"Missing '{e.args[0]}' attribute in <Agent> at position {agent_idx}.") from e
        except ValueError as e:
            raise ValueError(f"Type error in <Agent> at position {agent_idx}: {e}") from e

        # Process <Shapes> if present
        shapes_dict: ShapeDataType = {}
        for shape_idx, shape in enumerate(agent.findall("Shape")):
            # Validate required shape attributes
            try:
                shape_data = {
                    "Type": shape.attrib["Type"],
                    "Radius": float(shape.attrib["Radius"]),
                    "MaterialId": str(shape.attrib["MaterialId"]),
                    "Position": fun.from_string_to_tuple(shape.attrib["Position"]),
                }
            except KeyError as e:
                raise ValueError(
                    f"Missing '{e.args[0]}' attribute in <Shape> at position {shape_idx} under <Agent> with Id={agent_data['Id']}."
                ) from e
            except ValueError as e:
                raise ValueError(f"Type error in <Shape> at position {shape_idx} under <Agent> with Id={agent_data['Id']}: {e}") from e
            # Assign a unique name to each shape (e.g., disk0, disk1, ...)
            shape_name = f"disk{shape_idx}"
            shapes_dict[shape_name] = shape_data
        agent_data["Shapes"] = shapes_dict

        # Assign a unique name to each agent (e.g., Agent0, Agent1, ...)
        agent_name = f"Agent{agent_idx}"
        crowd_dict["Agents"][agent_name] = agent_data

    return crowd_dict


def dynamic_xml_to_dict(xml_data: str) -> DynamicCrowdDataType:
    """
    Convert an XML string representing crowd dynamic parameters into a dictionary, with validation of structure and attribute types.

    Parameters
    ----------
    xml_data : str
        A string containing XML data.

    Returns
    -------
    DynamicCrowdDataType
        A dictionary representation of the XML data.

    Raises
    ------
    ValueError
        If the XML structure or attribute types are incorrect.
    """
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        raise ValueError(f"Malformed XML: {e}") from e

    agents: DynamicCrowdDataType = {}

    for agent_idx, agent in enumerate(root.findall("Agent")):
        # Validate agent Id
        try:
            agent_id = int(agent.attrib["Id"])
        except KeyError as e:
            raise ValueError(f"Missing 'Id' attribute in <Agent> at position {agent_idx}.") from e
        except ValueError as e:
            raise ValueError(f"Invalid 'Id' value in <Agent> at position {agent_idx}: {e}") from e

        # Extract and validate kinematics
        kinematics = agent.find("Kinematics")
        if kinematics is None:
            raise ValueError(f"Missing <Kinematics> section for <Agent> with Id={agent_id}.")
        try:
            position_str = kinematics.attrib["Position"]
            velocity_str = kinematics.attrib["Velocity"]
            theta_str = kinematics.attrib["theta"]
            omega_str = kinematics.attrib["omega"]
        except KeyError as e:
            raise ValueError(f"Missing '{e.args[0]}' attribute in <Kinematics> for <Agent> with Id={agent_id}.") from e
        try:
            kinematics_dict = {
                "Position": fun.from_string_to_tuple(position_str),
                "Velocity": fun.from_string_to_tuple(velocity_str),
                "theta": float(theta_str),
                "omega": float(omega_str),
            }
        except ValueError as e:
            raise ValueError(f"Type error in <Kinematics> for <Agent> with Id={agent_id}: {e}") from e

        # Extract and validate dynamics
        dynamics = agent.find("Dynamics")
        if dynamics is None:
            raise ValueError(f"Missing <Dynamics> section for <Agent> with Id={agent_id}.")
        try:
            fp_str = dynamics.attrib["Fp"]
            mp_str = dynamics.attrib["Mp"]
        except KeyError as e:
            raise ValueError(f"Missing '{e.args[0]}' attribute in <Dynamics> for <Agent> with Id={agent_id}.") from e
        try:
            dynamics_dict = {
                "Fp": fun.from_string_to_tuple(fp_str),
                "Mp": float(mp_str),
            }
        except ValueError as e:
            raise ValueError(f"Type error in <Dynamics> for <Agent> with Id={agent_id}: {e}") from e

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
    Convert an XML string representing geometric data into a dictionary, with strict validation of structure and attribute types.

    Parameters
    ----------
    xml_data : str
        A string containing XML data.

    Returns
    -------
    GeometryDataType
        A dictionary representation of the XML data.

    Raises
    ------
    ValueError
        If the XML structure or attribute types are incorrect.
    """
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        raise ValueError(f"Malformed XML: {e}") from e

    # --- Extract and validate dimensions ---
    dimensions = root.find("Dimensions")
    if dimensions is None:
        raise ValueError("Missing required <Dimensions> section in XML.")

    try:
        dimensions_dict = {"Lx": float(dimensions.attrib["Lx"]), "Ly": float(dimensions.attrib["Ly"])}
    except KeyError as e:
        raise ValueError(f"Missing '{e.args[0]}' attribute in <Dimensions>.") from e
    except ValueError as e:
        raise ValueError(f"Type error in <Dimensions>: {e}") from e

    # --- Extract and validate walls and corners ---
    walls: dict[str, Any] = {}
    for wall_idx, wall in enumerate(root.findall("Wall")):
        # Validate required wall attributes
        try:
            wall_id = int(wall.attrib["Id"])
            id_material = str(wall.attrib["MaterialId"])
        except KeyError as e:
            raise ValueError(f"Missing '{e.args[0]}' attribute in <Wall> at position {wall_idx}.") from e
        except ValueError as e:
            raise ValueError(f"Type error in <Wall> at position {wall_idx}: {e}") from e

        # Validate corners section
        # corners_element = wall.find("Corners")

        corners: dict[str, dict[str, tuple[float, float]]] = {}
        for i, corner in enumerate(wall.findall("Corner")):
            try:
                coords = fun.from_string_to_tuple(corner.attrib["Coordinates"])
            except KeyError as e:
                raise ValueError(f"Missing 'Coordinates' attribute in <Corner> at position {i} for <Wall> with Id={wall_id}.") from e
            except ValueError as e:
                raise ValueError(f"Type error in 'Coordinates' of <Corner> at position {i} for <Wall> with Id={wall_id}: {e}") from e
            corners[f"Corner{i}"] = {"Coordinates": coords}

        walls[f"Wall{wall_id}"] = {
            "Id": wall_id,
            "MaterialId": id_material,
            "Corners": corners,
        }

    # --- Construct the final dictionary ---
    boundaries_dict = {"Geometry": {"Dimensions": dimensions_dict, "Wall": walls}}

    return boundaries_dict


def materials_xml_to_dict(xml_data: str) -> MaterialsDataType:
    """
    Convert an XML string representing material properties into a dictionary, with strict validation of structure and attribute types.

    Parameters
    ----------
    xml_data : str
        A string containing XML data.

    Returns
    -------
    MaterialsDataType
        A dictionary representation of the XML data.

    Raises
    ------
    ValueError
        If the XML structure or attribute types are incorrect.
    """
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        raise ValueError(f"Malformed XML: {e}") from e

    # --- Validate and extract Intrinsic materials ---
    intrinsic_element = root.find("Intrinsic")
    if intrinsic_element is None:
        raise ValueError("Missing required <Intrinsic> section in XML.")

    intrinsic_materials: IntrinsicMaterialDataType = []
    for idx, material in enumerate(intrinsic_element):
        try:
            instrinsic_material_dict = {
                "Id": str(material.attrib["Id"]),
                "YoungModulus": float(material.attrib["YoungModulus"]),
                "ShearModulus": float(material.attrib["ShearModulus"]),
            }
        except KeyError as e:
            raise ValueError(f"Missing '{e.args[0]}' attribute in <Material> at position {idx}.") from e
        except ValueError as e:
            raise ValueError(f"Type error in <Material> at position {idx}: {e}") from e

        intrinsic_materials.append(instrinsic_material_dict)

    # --- Validate and extract Binary contacts ---
    binary_element = root.find("Binary")
    if binary_element is None:
        raise ValueError("Missing required <Binary> section in XML.")

    binary_contacts: PairMaterialsDataType = []
    for idx, contact in enumerate(binary_element):
        try:
            contact_dict = {
                "Id1": str(contact.attrib["Id1"]),
                "Id2": str(contact.attrib["Id2"]),
                "GammaNormal": float(contact.attrib["GammaNormal"]),
                "GammaTangential": float(contact.attrib["GammaTangential"]),
                "KineticFriction": float(contact.attrib["KineticFriction"]),
            }
        except KeyError as e:
            raise ValueError(f"Missing '{e.args[0]}' attribute in <Contact> at position {idx}.") from e
        except ValueError as e:
            raise ValueError(f"Type error in <Contact> at position {idx}: {e}") from e

        binary_contacts.append(contact_dict)

    # --- Assemble the dictionary ---
    material_dict: MaterialsDataType = {
        "Materials": {
            "Intrinsic": {f"Material{id_material}": material for id_material, material in enumerate(intrinsic_materials)},
            "Binary": {f"Contact{i}": contact for i, contact in enumerate(binary_contacts)},
        }
    }

    return material_dict


def interactions_xml_to_dict(xml_data: str) -> InteractionsDataType:
    """
    Convert an XML string describing interactions into a nested dictionary structure, with validation of structure and attribute types.

    Parameters
    ----------
    xml_data : str
        A string containing XML data.

    Returns
    -------
    InteractionsDataType
        A dictionary representation of the XML data.

    Raises
    ------
    ValueError
        If the XML structure or attribute types are incorrect.
    """
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        raise ValueError(f"Malformed XML: {e}") from e

    interactions_dict: InteractionsDataType = {"Interactions": {}}

    # Iterate through all Agent elements in the XML
    for agent_idx, agent in enumerate(root.findall("Agent")):
        # Validate required attribute
        if "Id" not in agent.attrib:
            raise ValueError(f"Missing 'Id' attribute in <Agent> at position {agent_idx}.")
        try:
            agent_id = int(agent.attrib["Id"])
        except ValueError as e:
            raise ValueError(
                f"Invalid 'Id' value in <Agent> at position {agent_idx}: '{agent.attrib['Id']}' is not an integer."
            ) from e

        agent_key = f"Agent{agent_id}"
        interactions_dict["Interactions"][agent_key] = {"Id": agent_id, "NeighbouringAgents": {}}

        # Iterate through neighboring agents
        for neighbor_idx, neighbor_agent in enumerate(agent.findall("Agent")):
            if "Id" not in neighbor_agent.attrib:
                raise ValueError(f"Missing 'Id' attribute in <Agent> (neighbor) at position {neighbor_idx} under Agent {agent_id}.")
            try:
                neighbor_id = int(neighbor_agent.attrib["Id"])
            except ValueError as e:
                raise ValueError(
                    f"Invalid 'Id' value in <Agent> (neighbor) at position {neighbor_idx} under Agent {agent_id}: "
                    "'{neighbor_agent.attrib['Id']}' is not an integer."
                ) from e

            neighbor_key = f"Agent{neighbor_id}"
            interactions_dict["Interactions"][agent_key]["NeighbouringAgents"][neighbor_key] = {"Id": neighbor_id, "Interactions": {}}

            # Iterate through interactions
            for interaction_idx, interaction in enumerate(neighbor_agent.findall("Interaction")):
                required_attrs = ["ParentShape", "ChildShape", "TangentialRelativeDisplacement", "Fn", "Ft"]
                for attr in required_attrs:
                    if attr not in interaction.attrib:
                        raise ValueError(
                            f"Missing '{attr}' attribute in <Interaction> at position {interaction_idx} "
                            f"under Neighbor Agent {neighbor_id} of Agent {agent_id}."
                        )
                try:
                    parent_shape_id = int(interaction.attrib["ParentShape"])
                    child_shape_id = int(interaction.attrib["ChildShape"])
                    ft = fun.from_string_to_tuple(interaction.attrib["Ft"])
                    fn = fun.from_string_to_tuple(interaction.attrib["Fn"])
                    tangential_rel_displacement = fun.from_string_to_tuple(interaction.attrib["TangentialRelativeDisplacement"])
                except ValueError as e:
                    raise ValueError(
                        f"Type error in <Interaction> at position {interaction_idx} "
                        f"under Neighbor Agent {neighbor_id} of Agent {agent_id}: {e}"
                    ) from e

                interaction_key = f"Interaction_{parent_shape_id}_{child_shape_id}"
                interactions_dict["Interactions"][agent_key]["NeighbouringAgents"][neighbor_key]["Interactions"][interaction_key] = {
                    "ParentShape": parent_shape_id,
                    "ChildShape": child_shape_id,
                    "TangentialRelativeDisplacement": tangential_rel_displacement,
                    "Fn": fn,
                    "Ft": ft,
                }

    return interactions_dict
