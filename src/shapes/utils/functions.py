"""Contains utility functions for data processing and manipulation."""

import json
import pickle
from pathlib import Path
from typing import Any
from xml.dom.minidom import parseString

import numpy as np
import pandas as pd
import streamlit as st
from dicttoxml import dicttoxml
from numpy.typing import NDArray
from scipy.stats import truncnorm
from shapely.geometry import MultiPolygon
from streamlit.delta_generator import DeltaGenerator

import shapes.utils.constants as cst
from shapes.utils.typing_custom import BackupDataType, Sex, ShapeDataType


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

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    pickle.UnpicklingError
        If there is an error during the unpickling process.
    IOError
        If there is an issue opening or reading the file.
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

    Raises
    ------
    IOError
        If there is an issue opening or writing to the file.
    """
    with open(file_path, "w", encoding="utf8") as f:
        f.write(data)


@st.cache_data
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

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    pd.errors.EmptyDataError
        If the CSV file is empty.
    pd.errors.ParserError
        If there is an error parsing the CSV file.

    Notes
    -----
    - The caching mechanism provided by Streamlit (`@st.cache_data`) ensures that
      the data is only reloaded if the file changes, improving app performance.
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


def get_shapes_data(
    backup_data_type: BackupDataType,
    shapes_data: dict[str, dict[str, str | ShapeDataType]],
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
    shapes_data : dict[str, dict[str, str | ShapeDataType]]
        The shapes data to be serialized. This is typically a nested dictionary
        where keys are strings and values are either strings or `ShapeDataType` objects.

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
        xml_data = dicttoxml(shapes_data, custom_root="crowd", attr_type=False)

        # Parse the XML string
        dom = parseString(xml_data)

        # Pretty-print the XML with indentation and remove empty lines
        pretty_xml = dom.toprettyxml(indent="  ")
        data = "\n".join([line for line in pretty_xml.split("\n") if line.strip()])

        mime_type = "application/xml"

    elif backup_data_type == cst.BackupDataTypes.pickle.name:
        # Convert the dictionary to a pickle byte stream and hex-encode it
        data = pickle.dumps(shapes_data).hex()
        mime_type = "application/octet-stream"

    else:
        raise ValueError(f"Unsupported backup data type: {backup_data_type}")

    return data, mime_type


def extract_coordinates(multi_polygon: MultiPolygon) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Extract x and y coordinates from a MultiPolygon object.

    Parameters
    ----------
    multi_polygon : MultiPolygon
        A `shapely.geometry.MultiPolygon` object containing one or more polygons.

    Returns
    -------
    tuple[NDArray[np.float64], NDArray[np.float64]]
        A tuple of two NumPy arrays:
        - The first array contains the x-coordinates.
        - The second array contains the y-coordinates.

    Examples
    --------
    >>> from shapely.geometry import MultiPolygon, Polygon
    >>> from your_module import extract_coordinates
    >>> import numpy as np

    >>> # Create a sample MultiPolygon
    >>> poly1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 0)])
    >>> poly2 = Polygon([(2, 2), (3, 2), (3, 3), (2, 2)])
    >>> multi_poly = MultiPolygon([poly1, poly2])

    >>> # Extract coordinates
    >>> x_coords, y_coords = extract_coordinates(multi_poly)

    >>> print(x_coords)
    [0. 1. 1. 0. 2. 3. 3. 2.]

    >>> print(y_coords)
    [0. 0. 1. 0. 2. 2. 3. 2.]
    """
    all_x, all_y = [], []

    # Iterate through each polygon in the MultiPolygon
    for polygon in multi_polygon.geoms:
        x, y = polygon.exterior.xy  # Extract exterior boundary coordinates
        all_x.extend(x)
        all_y.extend(y)

    # Convert lists to NumPy arrays
    return np.array(all_x), np.array(all_y)


def filter_mesh_by_z_threshold(
    all_points: NDArray[np.float64], all_triangles: NDArray[np.float64], z_threshold: float = 0.3
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Filter a 3D mesh by removing vertices and triangles below a given z-coordinate threshold.

    Parameters
    ----------
    all_points : numpy.ndarray of shape (N, 3), dtype=np.float64
        An array representing the coordinates of the vertices in the mesh.
    all_triangles : numpy.ndarray of shape (M, 3), dtype=np.float64
        An array representing the indices of the vertices forming the triangles in the mesh.
    z_threshold : float
        The z-coordinate threshold below which vertices and associated triangles are removed.
        Default is 0.3.

    Returns
    -------
    filtered_points : numpy.ndarray of shape (P, 3), dtype=np.float64
        An array representing the coordinates of the filtered vertices.
    filtered_triangles : numpy.ndarray of shape (Q, 3), dtype=np.float64
        An array representing the indices of the vertices forming the filtered triangles.

    Notes
    -----
    - `N` is the number of vertices in the original mesh.
    - `M` is the number of triangles in the original mesh.
    - `P` and `Q` are the numbers of vertices and triangles remaining after filtering, respectively.
    """
    # Step 1: Identify valid vertices (z > threshold)
    valid_vertices_mask = all_points[:, 2] > z_threshold
    valid_indices = np.where(valid_vertices_mask)[0]

    # Step 2: Create a mapping from old vertex indices to new ones
    old_to_new_index = np.full(all_points.shape[0], -1)  # Initialize with -1 for invalid indices
    old_to_new_index[valid_indices] = np.arange(len(valid_indices))  # Map valid indices to new positions

    # Step 3: Filter triangles where all three vertices are valid
    valid_triangles_mask = np.all(np.isin(all_triangles, valid_indices), axis=1)
    filtered_triangles = all_triangles[valid_triangles_mask]

    # Step 4: Update triangle indices to reflect the new vertex indexing
    filtered_triangles = old_to_new_index[filtered_triangles]

    # Step 5: Filter the vertices based on the valid mask
    filtered_points = all_points[valid_vertices_mask]

    return filtered_points, filtered_triangles


def update_progress_bar(progress_bar: DeltaGenerator, status_text: DeltaGenerator, frac: float) -> None:
    """
    Update a progress bar and status text based on the given completion fraction.

    This function updates a progress bar and its associated status text to reflect
    the current progress of an operation. The progress is represented as a fraction
    between 0 and 1.

    Parameters
    ----------
    progress_bar : DeltaGenerator
        The Streamlit progress bar object to be updated. Typically created using
        `st.progress()`.
    status_text : DeltaGenerator
        The Streamlit text object to display the status message. Typically created
        using `st.text()`.
    frac : float
        A value between 0 and 1 representing the completion fraction of the task.
        For example, `frac=0.5` indicates 50% completion.

    Raises
    ------
    ValueError
        If `frac` is not between 0 and 1 (inclusive).
    """
    if not 0 <= frac <= 1:
        raise ValueError("The completion fraction 'frac' must be between 0 and 1 (inclusive).")

    # Update progress bar
    percent_complete = int(frac * 100.0)
    progress_bar.progress(percent_complete)

    # Update status text
    progress_text = "Operation in progress. Please wait. ⏳"
    status_text.text(f"{progress_text} {percent_complete}%")


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


def compute_moment_of_inertia(vertices: NDArray[np.float64], weight: float) -> float:
    """
    Compute the moment of inertia for a 2D polygon.

    This function calculates the moment of inertia (I_z) for a 2D shape
    represented as a polygon based on its vertices and weight. The calculation
    is performed using the second moment of area formula, assuming the polygon
    is in the XY-plane. For more details on the second moment of area, refer to:
    https://en.wikipedia.org/wiki/Second_moment_of_area

    Parameters
    ----------
    vertices : NDArray[np.float64]
        A 2D NumPy array of shape (N, 2), where each row represents the (x, y) coordinates
        of a vertex of the polygon. The last vertex should be identical to the first to close the polygon.
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
    N = len(vertices) - 1  # Last point is a repeat of the first

    I_z: float = 0.0
    for n in range(len(vertices) - 1):
        Pn = np.array(vertices[n])
        Pn1 = np.array(vertices[(n + 1) % N])
        cross_product_magnitude = abs(cross2d(Pn, Pn1))
        dot_product_terms = np.dot(Pn, Pn) + np.dot(Pn, Pn1) + np.dot(Pn1, Pn1)

        I_z += cross_product_magnitude * dot_product_terms

    moment_of_inertia: float = weight * I_z / 12.0
    return moment_of_inertia
