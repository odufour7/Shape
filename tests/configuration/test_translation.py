"""Tests for the translation methods of the Agent class."""

import pytest

import configuration.utils.constants as cst
from configuration.models.agents import Agent
from configuration.models.measures import AgentMeasures
from configuration.utils.typing_custom import Sex


@pytest.fixture
def agent() -> Agent:
    """
    Fixture to create an Agent instance for testing.

    Returns
    -------
    Agent
        An instance of Agent with predefined type and measures.
    """
    agent_type = cst.AgentTypes.pedestrian
    measures: dict[str, Sex | float] = {
        "sex": "male",
        "bideltoid_breadth": 45.0,
        "chest_depth": 25.0,
        "height": 180.0,
        "weight": 75.0,
    }
    agent_measures = AgentMeasures(agent_type=agent_type, measures=measures)
    return Agent(agent_type=agent_type, measures=agent_measures)


def test_translate_position(agent: Agent) -> None:
    """
    Test that the agent's position is correctly updated after translation of the 2D shapes.

    Parameters
    ----------
    agent : Agent
        The agent fixture.
    """
    initial_position = agent.get_position()
    agent.translate(30.0, 10.0)
    final_position = agent.get_position()
    assert abs(final_position.x - (initial_position.x + 30.0)) < 0.05, "The x-coordinate should have changed by 30.0."
    assert abs(final_position.y - (initial_position.y + 10.0)) < 0.05, "The y-coordinate should have changed by 10.0."

    initial_position = agent.get_position()
    agent.translate(-30.0, -10.0)
    final_position = agent.get_position()
    assert abs(final_position.x - (initial_position.x - 30.0)) < 0.05, "The x-coordinate should have changed by -30.0."
    assert abs(final_position.y - (initial_position.y - 10.0)) < 0.05, "The y-coordinate should have changed by -10.0."


def test_translate_body3d_xy(agent: Agent) -> None:
    """
    Test that the agent's 3D body centroid is correctly updated after translation in x and y.

    Parameters
    ----------
    agent : Agent
        The agent fixture.
    """
    initial_centroid = agent.get_centroid_body3D()
    agent.translate_body3D(30.0, 10.0, 0.0)
    final_centroid = agent.get_centroid_body3D()
    assert abs(final_centroid.x - (initial_centroid.x + 30.0)) < 0.05, "The x-coordinate should have changed by 30.0."
    assert abs(final_centroid.y - (initial_centroid.y + 10.0)) < 0.05, "The y-coordinate should have changed by 10.0."

    initial_centroid = agent.get_centroid_body3D()
    agent.translate_body3D(-30.0, -10.0, 0.0)
    final_centroid = agent.get_centroid_body3D()
    assert abs(final_centroid.x - (initial_centroid.x - 30.0)) < 0.05, "The x-coordinate should have changed by -30.0."
    assert abs(final_centroid.y - (initial_centroid.y - 10.0)) < 0.05, "The y-coordinate should have changed by -10.0."


def test_translate_body3d_z(agent: Agent) -> None:
    """
    Test that the agent's 3D body centroid and lowest height are correctly updated after translation in z.

    Parameters
    ----------
    agent : Agent
        The agent fixture.
    """
    initial_centroid = agent.get_centroid_body3D()
    initial_lowest_height = min(agent.shapes3D.shapes.keys())
    agent.translate_body3D(0.0, 0.0, 30.0)
    final_centroid = agent.get_centroid_body3D()
    final_lowest_height = min(agent.shapes3D.shapes.keys())
    assert abs(final_centroid.x - initial_centroid.x) < 0.05, "The x-coordinate should not have changed."
    assert abs(final_centroid.y - initial_centroid.y) < 0.05, "The y-coordinate should not have changed."
    assert abs(final_lowest_height - (initial_lowest_height + 30.0)) < 0.05, "The lowest height should have changed by 30.0."

    initial_centroid = agent.get_centroid_body3D()
    initial_lowest_height = min(agent.shapes3D.shapes.keys())
    agent.translate_body3D(0.0, 0.0, -30.0)
    final_centroid = agent.get_centroid_body3D()
    final_lowest_height = min(agent.shapes3D.shapes.keys())
    assert abs(final_centroid.x - initial_centroid.x) < 0.05, "The x-coordinate should not have changed."
    assert abs(final_centroid.y - initial_centroid.y) < 0.05, "The y-coordinate should not have changed."
    assert abs(final_lowest_height - (initial_lowest_height - 30.0)) < 0.05, "The lowest height should have changed by -30.0."
