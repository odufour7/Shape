"""Test interactions serialization/deserialization."""

from pathlib import Path

import pytest

import configuration.backup.crowd_to_dict as fun_dict
import configuration.backup.dict_to_xml_and_reverse as fun_xml
from configuration.models.crowd import Crowd


@pytest.fixture
def crowd(request: pytest.FixtureRequest) -> Crowd:
    """
    Fixture creating Crowd instances with parameterized agent counts and packing states.

    Parameters
    ----------
    request : pytest.FixtureRequest
        Contains tuple of (agent_count, should_pack) parameters

    Returns
    -------
    Crowd
        Configured instance with agents and optional force packing
    """
    agent_count, should_pack = request.param
    c = Crowd()
    c.create_agents(number_agents=agent_count)

    if should_pack:
        c.pack_agents_with_forces()

    return c


@pytest.mark.parametrize(
    "crowd", [(1, True), (1, False), (3, True), (3, False)], indirect=True, ids=["1_packed", "1_unpacked", "3_packed", "3_unpacked"]
)
def test_interactions_dict_xml_roundtrip(crowd: Crowd, tmp_path: Path) -> None:
    """
    Test XML serialization/deserialization.

    There are 4 scenarios:
        - 1 agent (packed/unpacked)
        - 3 agents (packed/unpacked)

    Parameters
    ----------
    crowd : Crowd
        The crowd fixture with agents and optional packing.
    tmp_path : Path
        Temporary directory for XML file storage.
    """
    # Original test logic remains unchanged
    interactions_dict = fun_dict.get_interactions_params(crowd)
    interactions_bytes = fun_xml.interactions_dict_to_xml(interactions_dict)

    xml_file = tmp_path / "test_interactions.xml"
    xml_file.write_bytes(interactions_bytes)

    content = xml_file.read_bytes()
    interactions_dict_new = fun_xml.interactions_xml_to_dict(content)

    assert interactions_dict_new == interactions_dict, (
        f"Data mismatch for {len(crowd.agents)} agents {'packed' if hasattr(crowd, 'packed_forces') else 'unpacked'}"
    )
