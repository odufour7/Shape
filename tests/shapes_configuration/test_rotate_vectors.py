"""
Unit tests for the rotate_vectors function.

Tests cover:
- Correct rotation for canonical angles (0, 90, 180, 270 degrees)
- Multiple vectors in the dictionary
- Empty dictionary
- Negative and non-integer angles
- Floating point precision handling
"""

import math

import pytest

from configuration.utils.functions import rotate_vectors


def vectors_close(vec1: tuple[float, float], vec2: tuple[float, float], tol: float = 1e-8) -> bool:
    """
    Help function to compare two 2D vectors for approximate equality.

    Parameters
    ----------
    vec1 : tuple[float, float]
    vec2 : tuple[float, float]
    tol : float
        Tolerance for comparison.

    Returns
    -------
    bool
    """
    return math.isclose(vec1[0], vec2[0], abs_tol=tol) and math.isclose(vec1[1], vec2[1], abs_tol=tol)


def test_rotate_0_degrees() -> None:
    """Test rotation by 0 degrees (should return original vectors)."""
    vectors = {"a": (1.0, 0.0), "b": (0.0, 1.0)}
    result = rotate_vectors(vectors, 0)
    for k in vectors:
        assert vectors_close(result[k], vectors[k])


def test_rotate_90_degrees() -> None:
    """Test rotation by 90 degrees."""
    vectors = {"x": (1.0, 0.0), "y": (0.0, 1.0)}
    expected = {"x": (0.0, 1.0), "y": (-1.0, 0.0)}
    result = rotate_vectors(vectors, 90)
    for k in vectors:
        assert vectors_close(result[k], expected[k])


def test_rotate_180_degrees() -> None:
    """Test rotation by 180 degrees."""
    vectors = {"v": (1.0, 0.0), "w": (0.0, 1.0)}
    expected = {"v": (-1.0, 0.0), "w": (0.0, -1.0)}
    result = rotate_vectors(vectors, 180)
    for k in vectors:
        assert vectors_close(result[k], expected[k])


def test_rotate_270_degrees() -> None:
    """Test rotation by 270 degrees (or -90 degrees)."""
    vectors = {"p": (1.0, 0.0), "q": (0.0, 1.0)}
    expected = {"p": (0.0, -1.0), "q": (1.0, 0.0)}
    result = rotate_vectors(vectors, 270)
    for k in vectors:
        assert vectors_close(result[k], expected[k])


def test_rotate_negative_angle() -> None:
    """Test rotation by a negative angle."""
    vectors = {"a": (1.0, 0.0)}
    theta = -90
    expected = {"a": (0.0, -1.0)}
    result = rotate_vectors(vectors, theta)
    assert vectors_close(result["a"], expected["a"])


def test_rotate_non_integer_angle() -> None:
    """Test rotation by a non-integer angle."""
    vectors = {"a": (1.0, 0.0)}
    theta = 45.0
    expected_x = math.cos(math.radians(45))
    expected_y = math.sin(math.radians(45))
    result = rotate_vectors(vectors, theta)
    assert math.isclose(result["a"][0], expected_x, abs_tol=1e-8)
    assert math.isclose(result["a"][1], expected_y, abs_tol=1e-8)


def test_rotate_empty_dict() -> None:
    """Test rotating an empty dictionary."""
    assert rotate_vectors({}, 45) == {}


def test_multiple_vectors() -> None:
    """Test rotating multiple vectors."""
    vectors = {"a": (1.0, 0.0), "b": (0.0, 1.0), "c": (1.0, 1.0), "d": (-1.0, -1.0)}
    theta = 90
    expected = {"a": (0.0, 1.0), "b": (-1.0, 0.0), "c": (-1.0, 1.0), "d": (1.0, -1.0)}
    result = rotate_vectors(vectors, theta)
    for k in vectors:
        assert vectors_close(result[k], expected[k])


def test_input_not_modified() -> None:
    """Test that input dictionary is not modified in place."""
    vectors = {"a": (1.0, 0.0)}
    vectors_copy = dict(vectors)
    rotate_vectors(vectors, 90)
    assert vectors == vectors_copy


def test_invalid_vector_format() -> None:
    """Test that invalid vector format (not a tuple of two floats) raises an error."""
    vectors = {"bad": (1.0,)}
    with pytest.raises(ValueError):
        rotate_vectors(vectors, 90)
