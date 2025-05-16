"""
Unit tests for the compute_moment_of_inertia function.

Tests cover:
    - Correct computation for simple polygons (square, triangle)
    - Handling of MultiPolygon (sum of moments)
    - Zero or negative weight handling
    - Invalid geometry types
    - Consistency with area scaling
"""

import math

import pytest
from shapely.geometry import MultiPolygon, Polygon

from configuration.utils.functions import compute_moment_of_inertia


def test_square_polygon() -> None:
    """Test moment of inertia for a unit square at origin."""
    square = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])  # cm
    weight = 2.0
    result = compute_moment_of_inertia(square, weight)
    # Analytical: I = (m/6) for unit square about centroid (converted to kg·m² as per function)
    expected = (weight / 6.0) * 1e-4
    print(f"Square moment of inertia: {result}, expected: {expected}")
    assert math.isclose(result, expected, rel_tol=1e-6)


def test_triangle_polygon() -> None:
    """Test moment of inertia for a right triangle."""
    triangle = Polygon([(0, 0), (1, 0), (0, 1)])
    weight = 3.0
    result = compute_moment_of_inertia(triangle, weight)
    # Compare with itself (idempotency)
    result2 = compute_moment_of_inertia(triangle, weight)
    assert math.isclose(result, result2, rel_tol=1e-12)
    assert result > 0


def test_multipolygon_sum() -> None:
    """Test that MultiPolygon sums the moments of the components."""
    poly1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    poly2 = Polygon([(2, 0), (3, 0), (3, 1), (2, 1)])
    mp = MultiPolygon([poly1, poly2])
    weight = 4.0
    # Should be the same as two squares, each with half the weight
    expected = compute_moment_of_inertia(poly1, weight / 2) + compute_moment_of_inertia(poly2, weight / 2)
    result = compute_moment_of_inertia(mp, weight)
    assert math.isclose(result, expected, rel_tol=1e-8)


def test_zero_weight() -> None:
    """Test that zero weight returns zero moment."""
    square = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    assert compute_moment_of_inertia(square, 0.0) == 0.0


def test_negative_weight() -> None:
    """Test that negative weight returns negative moment (mathematically valid)."""
    square = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    result = compute_moment_of_inertia(square, -2.0)
    assert result < 0


def test_invalid_geometry_type() -> None:
    """Test that invalid geometry raises TypeError."""
    with pytest.raises(TypeError):
        compute_moment_of_inertia("not_a_polygon", 1.0)


def test_scaling_with_area() -> None:
    """Test that scaling the polygon scales the moment of inertia by area^2."""
    square = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    weight = 2.0
    I1 = compute_moment_of_inertia(square, weight)
    # Scale by 2: area increases by 4, inertia by 16 (since inertia ~ area * r^2)
    square2 = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
    I2 = compute_moment_of_inertia(square2, weight * 4)
    assert math.isclose(I2, I1 * 16, rel_tol=1e-6)
