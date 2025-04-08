"""Contains utility functions for data processing and manipulation."""

import numpy as np
from numpy.typing import NDArray
from shapely.geometry import MultiPolygon
from streamlit.delta_generator import DeltaGenerator


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
