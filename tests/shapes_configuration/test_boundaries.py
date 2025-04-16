"""Test loading and saving of boundaries parameters in XML format."""

from pathlib import Path

import pytest
from pytest_lazyfixture import lazy_fixture

import configuration.backup.dict_to_xml_and_reverse as fun_xml
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
                    "Id": 0,
                    "MaterialId": 0,
                    "Corners": {
                        "Corner0": {"Coordinates": (0.0, 0.0)},
                        "Corner1": {"Coordinates": (0.0, 0.0)},
                        "Corner2": {"Coordinates": (0.0, 0.0)},
                        "Corner3": {"Coordinates": (0.0, 0.0)},
                        "Corner4": {"Coordinates": (0.0, 0.0)},
                    },
                },
                "Wall1": {
                    "Id": 1,
                    "MaterialId": 0,
                    "Corners": {
                        "Corner0": {"Coordinates": (0.0, 0.0)},
                        "Corner1": {"Coordinates": (0.0, 0.0)},
                        "Corner2": {"Coordinates": (0.0, 0.0)},
                        "Corner3": {"Coordinates": (0.0, 0.0)},
                        "Corner4": {"Coordinates": (0.0, 0.0)},
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
                    "Id": 0,
                    "MaterialId": 0,
                    "Corners": {
                        "Corner0": {"Coordinates": (0.0, 0.0)},
                        "Corner1": {"Coordinates": (0.0, 0.0)},
                        "Corner2": {"Coordinates": (0.0, 0.0)},
                        "Corner3": {"Coordinates": (0.0, 0.0)},
                        "Corner4": {"Coordinates": (0.0, 0.0)},
                    },
                },
            },
        },
    }


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
    xml_data = fun_xml.geometry_dict_to_xml(boundaries_dict)

    # Save XML to a temporary file
    temp_file_path = Path(__file__).resolve().parent / output_file_name
    with open(temp_file_path, "wb") as file:
        file.write(xml_data)

    # Read back the XML file and convert it back to a dictionary
    with open(temp_file_path, "r", encoding="utf-8") as file:
        loaded_xml_data = file.read()

    # Parse the XML string back to a dictionary
    parsed_boundaries = fun_xml.geometry_xml_to_dict(loaded_xml_data)

    # Assert that the original dictionary matches the parsed dictionary
    assert boundaries_dict == parsed_boundaries
