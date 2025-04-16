"""Test dynamic parameters loading and saving functions."""

from pathlib import Path

import pytest
from pytest_lazyfixture import lazy_fixture

import configuration.backup.dict_to_xml_and_reverse as fun_xml
from configuration.utils.typing_custom import DynamicCrowdDataType


@pytest.fixture
def dynamical_parameters_crowd() -> DynamicCrowdDataType:
    """Fixture to provide dynamic parameters for the crowd."""
    return {
        "Agents": {
            "Agent0": {
                "Id": 0,
                "Kinematics": {
                    "Position": (1.98663, 0.967745),
                    "Velocity": (0.0, 0.0),
                    "theta": 0.522024,
                    "omega": 0,
                },
                "Dynamics": {
                    "Fp": (55.749972, 225.838348),
                    "Mp": 0.49610395982099087,
                },
            },
            "Agent1": {
                "Id": 1,
                "Kinematics": {
                    "Position": (2.68599, 0.981293),
                    "Velocity": (0.0, 0.0),
                    "theta": -0.23153,
                    "omega": 0,
                },
                "Dynamics": {
                    "Fp": (52.4756752, 187.62116),
                    "Mp": -0.027266558433860527,
                },
            },
        }
    }


@pytest.mark.parametrize(
    "dynamical_parameters_crowd_dict",
    [lazy_fixture("dynamical_parameters_crowd")],
)
def test_dynamic_parameters_dict_to_xml_and_back(dynamical_parameters_crowd_dict: DynamicCrowdDataType, tmp_path: Path) -> None:
    """
    Test the loading and saving of dynamic parameters in XML format.

    This test converts a dictionary to XML, saves it to a temporary file, reads it back, and ensures
    that the parsed dictionary matches the original.
    """
    # Convert the dictionary to XML format
    xml_data = fun_xml.dynamic_dict_to_xml(dynamical_parameters_crowd_dict)

    # Save XML to a temporary file
    temp_file_path = tmp_path / "output_dynamic_crowd.xml"
    with open(temp_file_path, "wb") as file:
        file.write(xml_data)

    # Read back the XML file and convert it back to a dictionary
    with open(temp_file_path, "r", encoding="utf-8") as file:
        loaded_xml_data = file.read()

    # Parse the XML string back into a dictionary
    parsed_data = fun_xml.dynamic_xml_to_dict(loaded_xml_data)

    # Assert that the parsed dictionary matches the original one
    assert parsed_data == dynamical_parameters_crowd_dict, "Parsed data does not match original data."
