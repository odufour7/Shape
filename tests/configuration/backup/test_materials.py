"""Test the loading and saving of material parameters in XML format."""

from pathlib import Path

import pytest
from pytest_lazyfixture import lazy_fixture

import configuration.backup.dict_to_xml_and_reverse as fun_xml
from configuration.utils.typing_custom import MaterialsDataType


@pytest.fixture
def materials_dict() -> MaterialsDataType:
    """
    Fixture to provide material parameters for testing.

    Returns
    -------
    MaterialsDataType
        A dictionary containing material parameters, including intrinsic properties
        and binary contact properties between different materials.
    """
    return {
        "Materials": {
            "Intrinsic": {
                "Material0": {"Id": "Steel", "YoungModulus": 68.0, "ShearModulus": 25.5},
                "Material1": {"Id": "Aluminum", "YoungModulus": 200.0, "ShearModulus": 79.3},
                "Material2": {"Id": "Copper", "YoungModulus": 116, "ShearModulus": 41.4},
            },
            "Binary": {
                "Contact0": {
                    "Id1": "Steel",
                    "Id2": "Aluminum",
                    "GammaNormal": 1.3 * 10**4,
                    "GammaTangential": 1.3 * 10**4,
                    "KineticFriction": 0.5,
                },
                "Contact1": {
                    "Id1": "Steel",
                    "Id2": "Copper",
                    "GammaNormal": 1.3 * 10**4,
                    "GammaTangential": 1.3 * 10**4,
                    "KineticFriction": 0.5,
                },
                "Contact2": {
                    "Id1": "Aluminum",
                    "Id2": "Copper",
                    "GammaNormal": 1.3 * 10**4,
                    "GammaTangential": 1.3 * 10**4,
                    "KineticFriction": 0.5,
                },
                "Contact3": {
                    "Id1": "Aluminum",
                    "Id2": "Aluminum",
                    "GammaNormal": 1.3 * 10**4,
                    "GammaTangential": 1.3 * 10**4,
                    "KineticFriction": 0.5,
                },
                "Contact4": {
                    "Id1": "Copper",
                    "Id2": "Copper",
                    "GammaNormal": 1.3 * 10**4,
                    "GammaTangential": 1.3 * 10**4,
                    "KineticFriction": 0.5,
                },
                "Contact5": {
                    "Id1": "Steel",
                    "Id2": "Steel",
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

    This test converts a dictionary to XML, saves it to a temporary file, reads it back,
    and ensures that the parsed dictionary matches the original.

    Parameters
    ----------
    materials_dict_fixture : MaterialsDataType
        A fixture containing material parameters for testing.
    tmp_path : Path
        A temporary directory provided by pytest for file operations.
    """
    # Convert the dictionary to XML format
    xml_data = fun_xml.materials_dict_to_xml(materials_dict_fixture)

    # Save XML to a temporary file
    temp_file_path = tmp_path / "output_materials.xml"
    with open(temp_file_path, "wb") as file:
        file.write(xml_data)

    # Read back the XML file and convert it back to a dictionary
    with open(temp_file_path, "r", encoding="utf-8") as file:
        loaded_xml_data = file.read()

    # Parse the XML string back into a dictionary
    parsed_data = fun_xml.materials_xml_to_dict(loaded_xml_data)

    # Assert that the parsed dictionary matches the original one
    assert parsed_data == materials_dict_fixture, (
        f"Parsed data does not match original data.\nExpected: {materials_dict_fixture}\nGot: {parsed_data}"
    )
