"""Contains utility functions for data processing and manipulation."""

import itertools

import numpy as np
from numpy.typing import NDArray
from scipy.stats import truncnorm
from shapely.geometry import Polygon

import configuration.utils.constants as cst
from configuration.utils.typing_custom import IntrinsicMaterialDataType, MaterialsDataType, PairMaterialsDataType, Sex


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
            "id": id_material,
            "name": material,
            "young_modulus": getattr(cst, f"YOUNG_MODULUS_{material.upper()}"),
            "poisson_ratio": getattr(cst, f"POISSON_RATIO_{material.upper()}"),
        }
        for id_material, material in enumerate(cst.MaterialNames.__members__.keys())
    }

    # Binary material properties (pairwise interactions)
    binary_materials: PairMaterialsDataType = {
        f"Contact{id_contact}": {
            "id1": id1,
            "id2": id2,
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


def rotate_vectors(vector_dict: dict[str, tuple[float, float]], theta: float) -> dict[str, tuple[float, float]]:
    """
    Rotate 2D vectors in a dictionary by a given angle.

    Parameters
    ----------
    vector_dict : dict[str, tuple[float, float]]
        A dictionary where each key maps to a 2D vector represented as a tuple (x, y).
    theta : float
        The angle in degrees by which to rotate the vectors.

    Returns
    -------
    dict[str, tuple[float, float]]
        A dictionary with the same keys, where each vector has been rotated by the given angle.
    """
    theta_rad = np.radians(theta)  # Convert angle to radians

    rotated_dict = {}
    for key, (x, y) in vector_dict.items():
        # Apply rotation matrix
        x_rot = x * np.cos(theta_rad) - y * np.sin(theta_rad)
        y_rot = x * np.sin(theta_rad) + y * np.cos(theta_rad)
        rotated_dict[key] = (x_rot, y_rot)

    return rotated_dict
