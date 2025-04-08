"""Contains utility functions for data processing and manipulation."""

import json
import pickle
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from xml.dom import minidom

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy.stats import truncnorm
from shapely.geometry import Polygon

import configuration.utils.constants as cst
from configuration.utils.typing_custom import BackupDataType, CrowdDataType, Sex, ShapeDataType


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


def save_xml(data: str, file_path: Path) -> None:
    """
    Save data to an XML file.

    This function writes a string containing XML data to a specified file.
    The file is saved with UTF-8 encoding to ensure proper handling of
    special characters.

    Parameters
    ----------
    data : str
        A string containing the XML data to be saved.
    file_path : Path
        A `Path` object representing the path where the XML file will be saved.
    """
    with open(file_path, "w", encoding="utf8") as f:
        f.write(data)


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


def wrap_angle(angle: float) -> float:
    """
    Wrap an angle to the range [-180, 180).

    Parameters
    ----------
    angle : float
        The angle in degrees to be wrapped. This can be any real number.

    Returns
    -------
    float
        The wrapped angle in the range [-180, 180).
    """
    return (angle + 180.0) % 360.0 - 180.0


def dict_to_xml(crowd_dict: CrowdDataType) -> ET.Element:
    """
    Convert a dictionary to an XML element.

    Parameters
    ----------
    crowd_dict : dict
        A dictionary containing crowd data with agents and their associated shapes.
        The dictionary should have the following structure:
            {
                "Agents": {
                    "AgentName": {
                        "type": str,
                        "id": int,
                        "mass": float,
                        "moi": float,
                        "FloorDamping": float,
                        "AngularDamping": float,
                        "Shapes": {
                            "ShapeName": {
                                "type": str,
                                "radius": float,
                                "material": str,
                                "x": float,
                                "y": float
                            }
                        }
                    }
                }
            }

    Returns
    -------
    ET.Element
        The root XML element representing the crowd data, with nested elements for agents and shapes.
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
            # Create a <Shape> element with attributes
            ET.SubElement(
                shapes,
                "Shape",
                {
                    "type": shape_data["type"],
                    "radius": str(shape_data["radius"]),
                    "material": str(shape_data["material"]),
                    "x": str(shape_data["x"]),
                    "y": str(shape_data["y"]),
                },
            )

    return root


def prettify_xml(elem: ET.Element) -> str:
    """
    Convert an XML element into a pretty-printed XML string with proper indentation.

    Parameters
    ----------
    elem : ET.Element
        The root XML element to be converted into a pretty-printed string.

    Returns
    -------
    str
        A pretty-printed XML string representation of the input element.
    """
    rough_string = ET.tostring(elem, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")


def get_shapes_data(
    backup_data_type: BackupDataType,
    shapes_data: CrowdDataType,
) -> tuple[str, str]:
    """
    Serialize shapes data into the specified backup format.

    This function serializes a given shapes data dictionary into one of the
    supported formats: JSON, XML, or Pickle. It also returns the corresponding
    MIME type for the serialized data.

    Parameters
    ----------
    backup_data_type : BackupDataType
        The format in which to serialize the data. Supported types are:
        - `'json'` for JSON serialization.
        - `'xml'` for XML serialization.
        - `'pickle'` for Pickle serialization.
    shapes_data : CrowdDataType
        The shapes data to be serialized.

    Returns
    -------
    tuple[str, str]
        A tuple containing:
        - The serialized data as a string (or hex-encoded string for Pickle).
        - The corresponding MIME type for the serialized data: (`"application/json"` for JSON,
        `"application/xml"` for XML,`"application/octet-stream"` for Pickle).

    Raises
    ------
    ValueError
        If the provided `backup_data_type` is not supported.
    """
    if backup_data_type == cst.BackupDataTypes.json.name:
        # Convert the dictionary to JSON
        data = json.dumps(shapes_data, indent=4)
        mime_type = "application/json"

    elif backup_data_type == cst.BackupDataTypes.xml.name:
        # Convert the dictionary to XML
        mime_type = "application/xml"

        # Convert the dictionary to XML
        xml_tree = dict_to_xml(shapes_data)

        # Prettify and write the XML to a file
        data = prettify_xml(xml_tree)

    elif backup_data_type == cst.BackupDataTypes.pickle.name:
        # Convert the dictionary to a pickle byte stream and hex-encode it
        data = pickle.dumps(shapes_data).hex()
        mime_type = "application/octet-stream"

    else:
        raise ValueError(f"Unsupported backup data type: {backup_data_type}")

    return data, mime_type


def xml_to_dict(xml_file: str) -> CrowdDataType:
    """
    Convert an XML file to a Python dictionary.

    Parameters
    ----------
    xml_file : str
        Path to the XML file to be converted.

    Returns
    -------
    dict
        A dictionary representation of the XML file with the same format as the input dictionary.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Initialize the main dictionary structure
    crowd_dict: CrowdDataType = {"Agents": {}}

    # Iterate over each <Agent> element in the XML
    for agent in root.findall("Agent"):
        agent_data: dict[str, int | float | ShapeDataType] = {
            "type": agent.get("type"),
            "id": int(agent.get("id") or 0),
            "mass": float(agent.get("mass") or 0.0),
            "moi": float(agent.get("moi") or 0.0),
            "FloorDamping": float(agent.get("FloorDamping") or 0.0),
            "AngularDamping": float(agent.get("AngularDamping") or 0.0),
            # "Shapes": {},
        }

        # Find <Shapes> element and process each <Shape> inside it
        shapes = agent.find("Shapes")
        if shapes is not None:
            shapes_dict: ShapeDataType = {}
            for i, shape in enumerate(shapes.findall("Shape"), start=1):
                shape_data = {
                    "type": shape.get("type"),
                    "radius": float(shape.get("radius")),
                    "material": shape.get("material"),
                    "x": float(shape.get("x")),
                    "y": float(shape.get("y")),
                }
                # Assign a unique name to each shape (e.g., disk1, disk2)
                shape_name = f"disk{i}"
                shapes_dict[shape_name] = shape_data
            agent_data["Shapes"] = shapes_dict

        # Assign a unique name to each agent (e.g., Agent0, Agent1)
        agent_name = f"Agent{len(crowd_dict['Agents'])}"
        crowd_dict["Agents"][agent_name] = agent_data

    return crowd_dict


def draw_from_trunc_normal(mean: float, std_dev: float, min_val: float, max_val: float) -> float:
    """
    Draw a sample from a truncated normal distribution.

    This function generates a random sample from a normal distribution that is truncated
    within the range [`min_val`, `max_val`]. The truncation ensures that the sample lies
    within the specified bounds.

    Parameters
    ----------
    mean : float
        The mean (center) of the normal distribution.
    std_dev : float
        The standard deviation (spread) of the normal distribution.
    min_val : float
        The lower bound of the truncated normal distribution.
    max_val : float
        The upper bound of the truncated normal distribution.

    Returns
    -------
    float
        A sample drawn from the truncated normal distribution.

    Raises
    ------
    ValueError
        If `std_dev` is less than or equal to zero, or if `min_val` is greater than or equal
        to `max_val`.
    """
    if std_dev <= 0:
        raise ValueError("Standard deviation must be greater than zero.")

    if min_val >= max_val:
        raise ValueError("min_val must be less than max_val.")

    # Calculate standardized bounds for truncation
    a = (min_val - mean) / std_dev
    b = (max_val - mean) / std_dev

    # Draw a sample from the truncated normal distribution
    return float(truncnorm.rvs(a, b, loc=mean, scale=std_dev))


def draw_sex(p: float) -> Sex:
    """
    Randomly draw a sex ("male" or "female") based on the input proportion of "male".

    Parameters
    ----------
    p : float
        A proportion value between 0 and 1 (inclusive), representing the likelihood of selecting "male".

    Returns
    -------
    Sex
        "male" if a randomly generated number is less than `p`; otherwise, "female".

    Raises
    ------
    ValueError
        If the probability `p` is not between 0 and 1 (inclusive).
    """
    # Check if the probability is between 0 and 1
    if not 0 <= p <= 1:
        raise ValueError("Probability p must be between 0 and 1.")

    # Draw a random number and return the sex
    return "male" if np.random.random() < p else "female"


def cross2d(Pn: NDArray[np.float64], Pn1: NDArray[np.float64]) -> float:
    """
    Compute the 2D cross product of two vectors.

    Parameters
    ----------
    Pn : NDArray[np.float64]
        A 1D NumPy array of shape (2,) representing the first 2D vector
        in the form [x, y].
    Pn1 : NDArray[np.float64]
        A 1D NumPy array of shape (2,) representing the second 2D vector
        in the form [x, y].

    Returns
    -------
    float
        The magnitude of the perpendicular vector to the plane formed by the input vectors.

    Notes
    -----
    - The 2D cross product is defined as:
      `Pn[0] * Pn1[1] - Pn[1] * Pn1[0]`
      This operation computes a scalar rather than a vector, as it is
      specific to 2D vectors.
    """
    return float(Pn[0] * Pn1[1] - Pn[1] * Pn1[0])


def compute_moment_of_inertia(geometric_shape: Polygon, weight: float) -> float:
    """
    Compute the moment of inertia for a 2D polygon.

    This function calculates the moment of inertia (I_z) for a 2D shape
    represented as a polygon based on its vertices and weight. The calculation
    is performed using the second moment of area formula, assuming the polygon
    is in the XY-plane. For more details on the second moment of area, refer to:
    https://en.wikipedia.org/wiki/Second_moment_of_area

    Parameters
    ----------
    geometric_shape : Polygon
        The geometrical representation of a pedestrian as a shapely Polygon object.
    weight : float
        The mass or weight of the shape in kilograms (kg).

    Returns
    -------
    float
        The computed moment of inertia for the shape in kg·m².

    Notes
    -----
    - The vertices must form a closed polygon. If not, the function assumes
      that the last vertex is implicitly connected to the first.
    - This function assumes a uniform mass distribution over the area of
      the polygon.
    """
    vertices = np.array(geometric_shape.exterior.coords)
    N: int = len(vertices) - 1  # Last point is a repeat of the first
    rho: float = weight / geometric_shape.area  # Density (mass per unit area)
    I_z: float = 0.0
    for n in range(len(vertices) - 1):
        Pn = np.array(vertices[n])
        Pn1 = np.array(vertices[(n + 1) % N])
        cross_product_magnitude = abs(cross2d(Pn, Pn1))
        dot_product_terms = np.dot(Pn, Pn) + np.dot(Pn, Pn1) + np.dot(Pn1, Pn1)

        I_z += cross_product_magnitude * dot_product_terms

    moment_of_inertia: float = rho * I_z / 12.0

    # convert to kg·m^2
    moment_of_inertia *= 1e-4

    return moment_of_inertia


def validate_material(material: str) -> None:
    """
    Validate if the given material is in MaterialNames.

    Parameters
    ----------
    material : str
        The material name to validate.

    Raises
    ------
    ValueError
        If the material is not in MaterialNames.
    """
    if material not in cst.MaterialNames.__members__:
        raise ValueError(
            f"Material '{material}' is not supported. Expected one of: {list(cst.MaterialNames.__members__.keys())}."
        )
