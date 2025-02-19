"""This module contains utility functions for data processing and manipulation."""

import pickle
from pathlib import Path
from typing import Any

import numpy as np
from shapely.geometry import MultiPolygon


def load_pickle(file_path: Path) -> Any:
    """Loads a pickle file from the specified path."""
    with open(file_path, "rb") as f:
        data = pickle.load(f)
    return data


def save_pickle(data, file_path: Path) -> None:
    """Saves data to a pickle file at the specified path."""
    with open(file_path, "wb") as f:
        pickle.dump(data, f)


def extract_coordinates(multi_polygon: MultiPolygon) -> tuple[np.ndarray, np.ndarray]:
    """Extracts the x and y coordinates of a MultiPolygon."""
    all_x, all_y = [], []
    for polygon in multi_polygon.geoms:
        x, y = polygon.exterior.xy
        all_x.extend(x)
        all_y.extend(y)
    return np.array(all_x), np.array(all_y)


def wrap_angle(angle: float) -> float:
    """Wrap an angle to the range [-π, π)."""
    return (angle + np.pi) % (2 * np.pi) - np.pi


def filter_mesh_by_z_threshold(
    all_points: np.ndarray, all_triangles: np.ndarray, z_threshold: float = 0.3
) -> tuple[np.ndarray, np.ndarray]:
    """Filters a 3D mesh by removing vertices and triangles associated with z-coordinates below a given threshold."""
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
