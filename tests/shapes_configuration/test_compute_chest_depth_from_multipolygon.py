"""
Unit tests for the compute_chest_depth_from_multipolygon function.

Tests cover:
- Simple MultiPolygon with known vertical depth
- MultiPolygon with two separated polygons
- Single Polygon wrapped in MultiPolygon
- Non-MultiPolygon input (error)
- Degenerate case: all points on a horizontal line (depth zero)
- Centroid shift invariance
- Irregular shape with known max vertical distance at similar x
"""

import numpy as np
import pytest
from shapely.geometry import MultiPolygon, Polygon

from configuration.utils.functions import compute_chest_depth_from_multipolygon  # Replace with your actual module


def test_simple_vertical_rectangle() -> None:
    """Test a single rectangle MultiPolygon where the chest depth is the rectangle's height."""
    # Rectangle: width=2, height=5
    rect = Polygon([(0, 0), (2, 0), (2, 5), (0, 5)])
    mp = MultiPolygon([rect])
    depth = compute_chest_depth_from_multipolygon(mp)
    assert np.isclose(depth, 5.0, atol=1e-6)


def test_two_rectangles_same_x() -> None:
    """Test two rectangles stacked vertically, depth should be distance between farthest points at same x."""
    rect1 = Polygon([(0, 0), (2, 0), (2, 1), (0, 1)])
    rect2 = Polygon([(0, 5), (2, 5), (2, 6), (0, 6)])
    mp = MultiPolygon([rect1, rect2])
    depth = compute_chest_depth_from_multipolygon(mp)
    assert np.isclose(depth, 6.0, atol=1e-6)


def test_single_point_horizontal_line() -> None:
    """All points have the same y, so depth should be zero."""
    # Horizontal line at y=1
    poly = Polygon([(0, 1), (1, 1), (2, 1)])
    mp = MultiPolygon([poly])
    depth = compute_chest_depth_from_multipolygon(mp)
    assert np.isclose(depth, 0.0, atol=1e-6)


def test_non_multipolygon_input() -> None:
    """Should raise ValueError for non-MultiPolygon input."""
    poly = Polygon([(0, 0), (1, 0), (1, 1)])
    with pytest.raises(ValueError):
        compute_chest_depth_from_multipolygon(poly)


def test_depth_includes_centroid_shift() -> None:
    """Test that centroid shift does not affect the result."""
    # Rectangle at (10, 10), height=3
    rect = Polygon([(10, 10), (12, 10), (12, 13), (10, 13)])
    mp = MultiPolygon([rect])
    depth = compute_chest_depth_from_multipolygon(mp)
    assert np.isclose(depth, 3.0, atol=1e-6)


def test_irregular_shape() -> None:
    """Test an irregular polygon where the max vertical distance is not between endpoints."""
    poly = Polygon([(0, 0), (1, 2), (2, 0), (1, -2)])
    mp = MultiPolygon([poly])
    # The maximum vertical distance at similar x is between (1,2) and (1,-2)
    depth = compute_chest_depth_from_multipolygon(mp)
    assert np.isclose(depth, 4.0, atol=1e-6)
