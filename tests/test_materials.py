"""Test the loading and saving of material parameters in XML format."""

from pathlib import Path

import pytest
from pytest_lazyfixture import lazy_fixture

import configuration.utils.loading_backup_functions as lb_fun
from configuration.utils.typing_custom import MaterialsDataType


@pytest.fixture
def materials_dict() -> MaterialsDataType:
    """Fixture to provide material parameters for testing."""
    return {
        "Materials": {
            "Intrinsic": {
                "Material0": {"id": 0, "name": "Steel", "YoungModulus": 68.0, "PoissonRatio": 25.5},
                "Material1": {"id": 1, "name": "Aluminum", "YoungModulus": 200.0, "PoissonRatio": 79.3},
                "Material2": {"id": 2, "name": "Copper", "YoungModulus": 116, "PoissonRatio": 41.4},
            },
            "Binary": {
                "Contact0": {
                    "id1": 0,
                    "id2": 1,
                    "GammaNormal": 1.3 * 10**4,
                    "GammaTangential": 1.3 * 10**4,
                    "KineticFriction": 0.5,
                },
                "Contact1": {
                    "id1": 0,
                    "id2": 2,
                    "GammaNormal": 1.3 * 10**4,
                    "GammaTangential": 1.3 * 10**4,
                    "KineticFriction": 0.5,
                },
                "Contact2": {
                    "id1": 1,
                    "id2": 2,
                    "GammaNormal": 1.3 * 10**4,
                    "GammaTangential": 1.3 * 10**4,
                    "KineticFriction": 0.5,
                },
            },
        }
    }


@pytest.mark.parametrize(
    "materials_dict_fixture",
    [lazy_fixture("materials_dict")],
)
def test_materials_dict_to_xml_and_back(materials_dict_fixture: MaterialsDataType, tmp_path: Path) -> None:
    """
    Test the loading and saving of material parameters in XML format.

    This test converts a dictionary to XML, saves it to a temporary file,
    reads it back, and ensures that the parsed dictionary matches the original.
    """
    # Convert the dictionary to XML format
    xml_data = lb_fun.materials_dict_to_xml(materials_dict_fixture)

    # Save XML to a temporary file
    temp_file_path = tmp_path / "output_materials.xml"
    with open(temp_file_path, "wb") as file:
        file.write(xml_data)

    # Read back the XML file and convert it back to a dictionary
    with open(temp_file_path, "r", encoding="utf-8") as file:
        loaded_xml_data = file.read()

    # Parse the XML string back into a dictionary
    parsed_data = lb_fun.materials_xml_to_dict(loaded_xml_data)

    # Assert that the parsed dictionary matches the original one
    assert parsed_data == materials_dict_fixture, (
        f"Parsed data does not match original data.\nExpected: {materials_dict_fixture}\nGot: {parsed_data}"
    )
