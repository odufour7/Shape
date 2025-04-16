"""
Unit tests for the compute_bideltoid_breadth_from_multipolygon function.

Tests cover:
- Simple MultiPolygon with known maximum horizontal breadth
- MultiPolygon with two separated polygons
- Single Polygon wrapped in MultiPolygon
- Non-MultiPolygon input (error)
- Degenerate case: all points on a vertical line (breadth zero)
"""

import numpy as np
import pytest
from shapely.geometry import MultiPolygon, Polygon

from configuration.utils.functions import compute_bideltoid_breadth_from_multipolygon


def test_simple_horizontal_rectangle() -> None:
    """Test a single rectangle MultiPolygon where the breadth is the rectangle's width."""
    # Rectangle: width=4, height=2
    rect = Polygon([(0, 0), (4, 0), (4, 2), (0, 2)])
    mp = MultiPolygon([rect])
    breadth = compute_bideltoid_breadth_from_multipolygon(mp)
    assert np.isclose(breadth, 4.0, atol=1e-6)


def test_two_rectangles_same_y() -> None:
    """Test two rectangles side by side, breadth should be distance between farthest points at same y."""
    rect1 = Polygon([(0, 0), (2, 0), (2, 1), (0, 1)])
    rect2 = Polygon([(5, 0), (7, 0), (7, 1), (5, 1)])
    mp = MultiPolygon([rect1, rect2])
    breadth = compute_bideltoid_breadth_from_multipolygon(mp)
    assert np.isclose(breadth, 7.0, atol=1e-6)


def test_single_point_vertical_line() -> None:
    """All points have the same x, so breadth should be zero."""
    # Vertical line at x=1
    poly = Polygon([(1, 0), (1, 1), (1, 2)])
    mp = MultiPolygon([poly])
    breadth = compute_bideltoid_breadth_from_multipolygon(mp)
    assert np.isclose(breadth, 0.0, atol=1e-6)


def test_non_multipolygon_input() -> None:
    """Should raise ValueError for non-MultiPolygon input."""
    poly = Polygon([(0, 0), (1, 0), (1, 1)])
    with pytest.raises(ValueError):
        compute_bideltoid_breadth_from_multipolygon(poly)


def test_breadth_includes_centroid_shift() -> None:
    """Test that centroid shift does not affect the result."""
    # Rectangle at (10, 10), width=3
    rect = Polygon([(10, 10), (13, 10), (13, 12), (10, 12)])
    mp = MultiPolygon([rect])
    breadth = compute_bideltoid_breadth_from_multipolygon(mp)
    assert np.isclose(breadth, 3.0, atol=1e-6)


def test_irregular_shape() -> None:
    """Test an irregular polygon where the max horizontal distance is not between endpoints."""
    poly = Polygon([(0, 0), (2, 1), (1, 2), (0, 1)])
    mp = MultiPolygon([poly])
    # The maximum horizontal distance at similar y is between (0,1) and (2,1)
    breadth = compute_bideltoid_breadth_from_multipolygon(mp)
    assert np.isclose(breadth, 2.0, atol=1e-6)
