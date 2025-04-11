"""Test loading and saving of boundaries parameters in XML format."""

from pathlib import Path

import pytest
from pytest_lazyfixture import lazy_fixture

import configuration.utils.loading_backup_functions as lb_fun
from configuration.utils.typing_custom import GeometryDataType


@pytest.fixture
def boundaries_dict_two_walls() -> GeometryDataType:
    """
    Provide a fixture containing boundary data for a geometry with two walls.

    Returns
    -------
    GeometryDataType
        A dictionary representing the geometry data, including dimensions and
        wall properties such as material ID and corner coordinates.
    """
    return {
        "Geometry": {
            "Dimensions": {"Lx": 6.08, "Ly": 5.08},
            "Wall": {
                "Wall0": {
                    "id": 0,
                    "IdMaterial": 0,
                    "Corners": {
                        "Corner0": {"x": 0.0, "y": 0.0},
                        "Corner1": {"x": 6.04, "y": 0.0},
                        "Corner2": {"x": 6.04, "y": 5.04},
                        "Corner3": {"x": 0.0, "y": 5.04},
                        "Corner4": {"x": 0.0, "y": 0.0},
                    },
                },
                "Wall1": {
                    "id": 1,
                    "IdMaterial": 0,
                    "Corners": {
                        "Corner0": {"x": 0.0, "y": 0.0},
                        "Corner1": {"x": 6.04, "y": 0.0},
                        "Corner2": {"x": 6.04, "y": 5.04},
                        "Corner3": {"x": 0.0, "y": 5.04},
                        "Corner4": {"x": 0.0, "y": 0.0},
                    },
                },
            },
        },
    }


@pytest.fixture
def boundaries_dict_one_wall() -> GeometryDataType:
    """
    Provide a fixture containing boundary data for a geometry with one wall.

    Returns
    -------
    GeometryDataType
        A dictionary representing the geometry data, including dimensions and
        wall properties such as material ID and corner coordinates.
    """
    return {
        "Geometry": {
            "Dimensions": {"Lx": 6.08, "Ly": 5.08},
            "Wall": {
                "Wall0": {
                    "id": 0,
                    "IdMaterial": 0,
                    "Corners": {
                        "Corner0": {"x": 0.0, "y": 0.0},
                        "Corner1": {"x": 6.04, "y": 0.0},
                        "Corner2": {"x": 6.04, "y": 5.04},
                        "Corner3": {"x": 0.0, "y": 5.04},
                        "Corner4": {"x": 0.0, "y": 0.0},
                    },
                },
            },
        },
    }


# Parametrize test cases using lazy_fixture
@pytest.mark.parametrize(
    "boundaries_dict, output_file_name",
    [
        (lazy_fixture("boundaries_dict_two_walls"), Path("output_boundaries_two_walls.xml")),
        (lazy_fixture("boundaries_dict_one_wall"), Path("output_boundaries_one_wall.xml")),
    ],
)
def test_geometry_dict_to_xml_and_back(boundaries_dict: GeometryDataType, output_file_name: Path) -> None:
    """Test the loading and saving of boundaries parameters in XML format."""
    # Convert dictionary to XML
    xml_data = lb_fun.geometry_dict_to_xml(boundaries_dict)

    # Save XML to a temporary file
    temp_file_path = Path(__file__).resolve().parent / output_file_name
    with open(temp_file_path, "wb") as file:
        file.write(xml_data)

    # Read back the XML file and convert it back to a dictionary
    with open(temp_file_path, "r", encoding="utf-8") as file:
        loaded_xml_data = file.read()

    # Parse the XML string back to a dictionary
    parsed_boundaries = lb_fun.geometry_xml_to_dict(loaded_xml_data)

    # Assert that the original dictionary matches the parsed dictionary
    assert boundaries_dict == parsed_boundaries
