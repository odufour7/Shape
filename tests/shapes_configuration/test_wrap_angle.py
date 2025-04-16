"""
Unit tests for the wrap_angle function.

Tests cover:
- Canonical angles (0, 180, -180, 360, -360, 720, -720)
- Angles just outside the bounds
- Negative and positive values
- Large and small angles
- Floating point precision
"""

import numpy as np

from configuration.utils.functions import wrap_angle


def test_zero_angle() -> None:
    """Test that 0 degrees wraps to 0."""
    assert wrap_angle(0.0) == 0.0


def test_positive_angles() -> None:
    """Test wrapping of positive angles."""
    assert wrap_angle(45.0) == 45.0
    assert wrap_angle(180.0) == -180.0
    assert wrap_angle(181.0) == -179.0
    assert wrap_angle(359.0) == -1.0
    assert wrap_angle(360.0) == 0.0
    assert wrap_angle(540.0) == -180.0
    assert wrap_angle(720.0) == 0.0


def test_negative_angles() -> None:
    """Test wrapping of negative angles."""
    assert wrap_angle(-45.0) == -45.0
    assert wrap_angle(-180.0) == -180.0
    assert wrap_angle(-181.0) == 179.0
    assert wrap_angle(-359.0) == 1.0
    assert wrap_angle(-360.0) == 0.0
    assert wrap_angle(-540.0) == -180.0
    assert wrap_angle(-720.0) == 0.0


def test_angles_just_outside_bounds() -> None:
    """Test angles just outside the -180 and 180 bounds."""
    assert np.isclose(wrap_angle(179.9999), 179.9999, atol=1e-6)
    assert np.isclose(wrap_angle(180.0001), -179.9999, atol=1e-6)
    assert np.isclose(wrap_angle(-179.9999), -179.9999, atol=1e-6)
    assert np.isclose(wrap_angle(-180.0001), 179.9999, atol=1e-6)


def test_large_angles() -> None:
    """Test very large positive and negative angles."""
    assert wrap_angle(123456.0) == ((123456.0 + 180.0) % 360.0) - 180.0
    assert wrap_angle(-987654.0) == ((-987654.0 + 180.0) % 360.0) - 180.0


def test_floating_point_precision() -> None:
    """Test floating point precision edge case."""
    assert np.isclose(wrap_angle(180.0000001), -179.9999999, atol=1e-7)
    assert np.isclose(wrap_angle(-180.0000001), 179.9999999, atol=1e-7)
