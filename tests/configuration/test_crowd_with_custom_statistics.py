"""Test the Crowd class with custom agent statistics."""

import numpy as np
import pytest

import configuration.utils.constants as cst
from configuration.models.crowd import Crowd
from configuration.models.measures import CrowdMeasures

# Constants for the test
NUMBER_AGENTS: int = 30
REPULSION_LENGTH: float = 5.0  # (cm)
DESIRED_DIRECTION: float = 90.0  # (degrees)
RANDOM_PACKING: bool = False

# Custom agent statistics for the test
AGENT_STATISTICS: dict[str, float] = {
    **cst.CrowdStat,
    "male_proportion": 0.4,
    "male_bideltoid_breadth_mean": 70.0,  # cm
    "male_bideltoid_breadth_std_dev": 3.0,  # cm
}


@pytest.fixture
def crowd() -> Crowd:
    """
    Fixture to create a Crowd instance with predefined measures and agents.

    Returns
    -------
    Crowd
        An instance of Crowd with agents created and packed.
    """
    crowd_measures = CrowdMeasures(agent_statistics=AGENT_STATISTICS)
    crowd = Crowd(measures=crowd_measures)
    crowd.create_agents(number_agents=NUMBER_AGENTS)
    crowd.pack_agents_with_forces()
    return crowd


def test_crowd_number_of_agents(crowd: Crowd) -> None:
    """
    Test that the crowd contains the expected number of agents.

    Parameters
    ----------
    crowd : Crowd
        The crowd fixture.
    """
    assert crowd.get_number_agents() == NUMBER_AGENTS, f"Expected {NUMBER_AGENTS} agents, but got {crowd.get_number_agents()} agents."


def test_crowd_statistics_means_and_proportion(crowd: Crowd) -> None:
    """
    Test that measured crowd statistics are close to the expected values.

    Parameters
    ----------
    crowd : Crowd
        The crowd fixture.
    """
    measured_stats = crowd.get_crowd_statistics()["measures"]
    for key, value in measured_stats.items():
        if "mean" in key and ("pedestrian" in key or "male" in key or "female" in key):
            expected = AGENT_STATISTICS[key]
            assert np.isclose(value, expected, rtol=0.1), f"Expected {key} to be close to {expected}, but got {value}."
        if key == "male_proportion":
            expected = AGENT_STATISTICS[key]
            assert np.isclose(value, expected, atol=0.4), f"Expected {key} to be close to {expected}, but got {value}."
