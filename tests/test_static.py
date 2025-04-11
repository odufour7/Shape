"""Test the loading and saving of static parameters for pedestrians in XML format."""

from pathlib import Path

import pytest
from pytest_lazyfixture import lazy_fixture

import configuration.utils.loading_backup_functions as lb_fun
from configuration.utils.typing_custom import StaticCrowdDataType


@pytest.fixture
def crowd_static_dict() -> StaticCrowdDataType:
    """Fixture to provide static parameters for pedestrians."""
    return {
        "Agents": {
            "Agent0": {
                "type": "pedestrian",
                "id": 0,
                "mass": 81.9,
                "MOI": 1.5757210663140804,
                "FloorDamping": 2.0,
                "AngularDamping": 5.0,
                "Shapes": {
                    "disk1": {"type": "circle", "radius": 0.08243320, "IdMaterial": 0, "x": -0.0926936, "y": 0.134223},
                    "disk2": {"type": "circle", "radius": 0.11335892, "IdMaterial": 0, "x": -0.0290297, "y": 0.0655972},
                    "disk3": {"type": "circle", "radius": 0.11850000, "IdMaterial": 0, "x": 0.0101824, "y": 0.00585743},
                    "disk4": {"type": "circle", "radius": 0.11335892, "IdMaterial": 0, "x": 0.0421113, "y": -0.058072},
                    "disk5": {"type": "circle", "radius": 0.08243320, "IdMaterial": 0, "x": 0.0694296, "y": -0.147606},
                },
            },
            "Agent1": {
                "type": "pedestrian",
                "id": 1,
                "mass": 66.8,
                "MOI": 1.0783859912302556,
                "FloorDamping": 2.0,
                "AngularDamping": 5.0,
                "Shapes": {
                    "disk1": {"type": "circle", "radius": 0.07234643, "IdMaterial": 0, "x": 0.0237954, "y": 0.152256},
                    "disk2": {"type": "circle", "radius": 0.09948800, "IdMaterial": 0, "x": 0.0219175, "y": 0.0641057},
                    "disk3": {"type": "circle", "radius": 0.10400000, "IdMaterial": 0, "x": 0.0100344, "y": -0.00236569},
                    "disk4": {"type": "circle", "radius": 0.09948800, "IdMaterial": 0, "x": -0.00902588, "y": -0.067145},
                    "disk5": {"type": "circle", "radius": 0.07234643, "IdMaterial": 0, "x": -0.0467214, "y": -0.146851},
                },
            },
        }
    }


@pytest.mark.parametrize(
    "crowd_static_dict_fixture",
    [lazy_fixture("crowd_static_dict")],
)
def test_static_parameters_pedestrians_dict_to_xml_and_back(
    crowd_static_dict_fixture: StaticCrowdDataType, tmp_path: Path
) -> None:
    """
    Test the loading and saving of static parameters for pedestrians in XML format.

    This test converts a dictionary to XML format, saves it to a temporary file,
    reads it back from the file, and ensures that the parsed dictionary matches the original.
    """
    # Convert the dictionary to XML format
    xml_data = lb_fun.static_parameters_pedestrians_dict_to_xml(crowd_static_dict_fixture)

    # Save XML to a temporary file
    temp_file_path = tmp_path / "output_static_crowd.xml"
    with open(temp_file_path, "wb") as file:
        file.write(xml_data)

    # Read back the XML file and convert it back to a dictionary
    with open(temp_file_path, "r", encoding="utf-8") as file:
        loaded_xml_data = file.read()

    # Parse the XML string back into a dictionary
    parsed_data = lb_fun.static_parameters_pedestrians_xml_to_dict(loaded_xml_data)

    # Assert that the parsed dictionary matches the original one
    assert parsed_data == crowd_static_dict_fixture, (
        f"Parsed data does not match original data.\nExpected: {crowd_static_dict_fixture}\nGot: {parsed_data}"
    )
