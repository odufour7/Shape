"""Test the loading and saving of static parameters for pedestrians in XML format."""

from pathlib import Path

import pytest
from pytest_lazyfixture import lazy_fixture

import configuration.backup.dict_to_xml_and_reverse as fun_xml
from configuration.utils.typing_custom import StaticCrowdDataType


@pytest.fixture
def crowd_static_dict() -> StaticCrowdDataType:
    """Fixture to provide static parameters for pedestrians."""
    return {
        "Agents": {
            "Agent0": {
                "Type": "pedestrian",
                "Id": 0,
                "Mass": 81.9,
                "Height": 1.8,
                "MomentOfInertia": 1.57,
                "FloorDamping": 2.0,
                "AngularDamping": 5.0,
                "Shapes": {
                    "disk0": {"Type": "disk", "Radius": 0.08, "MaterialId": "human_clothes", "Position": (-0.09, 0.13)},
                    "disk1": {"Type": "disk", "Radius": 0.11, "MaterialId": "human_clothes", "Position": (-0.02, 0.06)},
                    "disk2": {"Type": "disk", "Radius": 0.11, "MaterialId": "human_clothes", "Position": (0.01, 0.00)},
                    "disk3": {"Type": "disk", "Radius": 0.11, "MaterialId": "human_clothes", "Position": (0.04, -0.05)},
                    "disk4": {"Type": "disk", "Radius": 0.08, "MaterialId": "human_clothes", "Position": (0.06, -0.14)},
                },
            },
            "Agent1": {
                "Type": "pedestrian",
                "Id": 1,
                "Mass": 66.8,
                "Height": 1.8,
                "MomentOfInertia": 1.07,
                "FloorDamping": 2.0,
                "AngularDamping": 5.0,
                "Shapes": {
                    "disk0": {"Type": "disk", "Radius": 0.07, "MaterialId": "human_naked", "Position": (0.02, 0.15)},
                    "disk1": {"Type": "disk", "Radius": 0.09, "MaterialId": "human_naked", "Position": (0.02, 0.06)},
                    "disk2": {"Type": "disk", "Radius": 0.10, "MaterialId": "human_naked", "Position": (0.01, -0.00)},
                    "disk3": {"Type": "disk", "Radius": 0.09, "MaterialId": "human_naked", "Position": (-0.00, -0.06)},
                    "disk4": {"Type": "disk", "Radius": 0.07, "MaterialId": "human_naked", "Position": (-0.04, -0.14)},
                },
            },
        }
    }


@pytest.mark.parametrize(
    "crowd_static_dict_fixture",
    [lazy_fixture("crowd_static_dict")],
)
def test_static_parameters_pedestrians_dict_to_xml_and_back(crowd_static_dict_fixture: StaticCrowdDataType, tmp_path: Path) -> None:
    """
    Test the loading and saving of static parameters for pedestrians in XML format.

    This test converts a dictionary to XML format, saves it to a temporary file,
    reads it back from the file, and ensures that the parsed dictionary matches the original.
    """
    # Convert the dictionary to XML format
    xml_data = fun_xml.static_dict_to_xml(crowd_static_dict_fixture)

    # Save XML to a temporary file
    temp_file_path = tmp_path / "output_static_crowd.xml"
    with open(temp_file_path, "wb") as file:
        file.write(xml_data)

    # Read back the XML file and convert it back to a dictionary
    with open(temp_file_path, "r", encoding="utf-8") as file:
        loaded_xml_data = file.read()

    # Parse the XML string back into a dictionary
    parsed_data = fun_xml.static_xml_to_dict(loaded_xml_data)

    # Assert that the parsed dictionary matches the original one
    assert parsed_data == crowd_static_dict_fixture, (
        f"Parsed data does not match original data.\nExpected: {crowd_static_dict_fixture}\nGot: {parsed_data}"
    )
