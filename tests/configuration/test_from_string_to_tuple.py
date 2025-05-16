"""
Unit tests for the from_string_to_tuple function.

Tests cover:
    - Valid string inputs (with/without parentheses, with extra spaces)
    - Invalid formats (wrong number of elements, not a string, non-numeric)
    - Edge cases (negative numbers, scientific notation, leading/trailing whitespace)
"""

import pytest

from configuration.utils.functions import from_string_to_tuple


def test_valid_input_no_parentheses() -> None:
    """Test valid input without parentheses."""
    assert from_string_to_tuple("1.0, 2.0") == (1.0, 2.0)


def test_valid_input_with_parentheses() -> None:
    """Test valid input with parentheses."""
    assert from_string_to_tuple("(3.14, 2.72)") == (3.14, 2.72)


def test_valid_input_with_spaces() -> None:
    """Test valid input with extra spaces."""
    assert from_string_to_tuple("  4.0 ,   5.0 ") == (4.0, 5.0)


def test_valid_input_negative_numbers() -> None:
    """Test valid input with negative numbers."""
    assert from_string_to_tuple(" -1.5, -2.5 ") == (-1.5, -2.5)


def test_valid_input_scientific_notation() -> None:
    """Test valid input with scientific notation."""
    assert from_string_to_tuple("1e3, 2e-2") == (1000.0, 0.02)


def test_invalid_input_not_a_string() -> None:
    """Test that non-string input raises ValueError."""
    with pytest.raises(ValueError, match="Input must be a string."):
        from_string_to_tuple(123)


def test_invalid_input_wrong_number_of_elements() -> None:
    """Test that input with wrong number of elements raises ValueError."""
    with pytest.raises(ValueError, match="String must contain exactly two numbers separated by a comma."):
        from_string_to_tuple("1.0, 2.0, 3.0")

    with pytest.raises(ValueError, match="String must contain exactly two numbers separated by a comma."):
        from_string_to_tuple("1.0")


def test_invalid_input_non_numeric() -> None:
    """Test that non-numeric elements raise ValueError."""
    with pytest.raises(ValueError, match="Both elements must be convertible to float."):
        from_string_to_tuple("a, b")

    with pytest.raises(ValueError, match="Both elements must be convertible to float."):
        from_string_to_tuple("(1.0, b)")


def test_invalid_input_empty_string() -> None:
    """Test that empty string raises ValueError."""
    with pytest.raises(ValueError):
        from_string_to_tuple("")


def test_valid_input_trailing_comma_spaces() -> None:
    """Test input with trailing and leading whitespace and parentheses."""
    assert from_string_to_tuple(" (  6.0 ,  7.0 ) ") == (6.0, 7.0)
