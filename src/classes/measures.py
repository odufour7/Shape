"""This module contains the Measures class to store body measures dynamically based on agent type."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import get_args

import numpy as np

import src.utils.constants as cst
from src.utils import functions as fun
from src.utils.typing_custom import AgentPart, AgentType


@dataclass
class AgentMeasures:
    """Class to store body measures dynamically based on agent type"""

    agent_type: AgentType
    measures: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        """
        Validates the measures based on the agent type after the object is initialized.

        Raises:
            ValueError: If the agent type is not one of the allowed values.
            ValueError: If measures is not a dictionary.
            ValueError: If required measures for the agent type are missing.
            ValueError: If extra measures are provided for non-custom agent types.

        Validations performed:
            - Checks if the agent type is valid.
            - Ensures measures is a dictionary.
            - Determines required parts based on the agent type.
            - Validates that all required measures are present.
            - Validates that no extra measures are provided for non-custom agent types.
        """

        # Check if the agent type is valid
        if self.agent_type not in get_args(AgentType):
            allowed_values = ", ".join(get_args(AgentType))
            raise ValueError(f"Agent type should be one of: {allowed_values}.")

        # Check if measures is a dictionary
        if not isinstance(self.measures, dict):
            raise ValueError("measures should be a dictionary.")

        # Determine required parts based on the agent type
        if self.agent_type == cst.AgentTypes.pedestrian.name:
            required_parts = {part.name for part in cst.PedestrianParts}
        elif self.agent_type == cst.AgentTypes.bike.name:
            required_parts = {part.name for part in cst.BikeParts}
        elif self.agent_type == cst.AgentTypes.custom.name:
            required_parts = set()  # Custom agents have no predefined required parts
        else:
            raise ValueError(f"Unknown agent type: {self.agent_type}")

        # Validate that all required measures are present
        missing_parts = required_parts - self.measures.keys()
        if missing_parts:
            raise ValueError(f"Missing measures for {self.agent_type.value}: {', '.join(missing_parts)}")

        # Validate that no extra measures are provided
        extra_parts = self.measures.keys() - required_parts
        if extra_parts and self.agent_type != cst.AgentTypes.custom.name:
            raise ValueError(f"Extra measures provided for {self.agent_type.value}: {', '.join(extra_parts)}")

    def number_of_measures(self) -> int:
        """
        Return the number of measures stored.

        Returns:
            int: The number of measures stored in the 'measures' attribute.
        """

        return len(self.measures)


@dataclass
class CrowdMeasures:
    """Class to store crowd measures based on agent type"""

    # ANSURII dataset by default (for men and women)
    default_database: dict[int, dict[str, float]] = field(default_factory=dict)
    custom_database: dict[int, dict[str, float]] = field(default_factory=dict)
    agent_statistics: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        """
        Validates the crowd measures after the dataclass initialization.

        This method performs the following validations and operations:
        1. Ensures that `default_database`, `custom_database`, and `agent_statistics` are dictionaries.
        2. Loads the ANSURII dataset into the `default_database` from a pickle file located in the data directory.
        3. Checks if the `agent_statistics` dictionary contains statistics for all required parts of the crowd.
           Raises a ValueError if any required statistics are missing.

        Raises:
            ValueError: If `default_database`, `custom_database`, or `agent_statistics` are not dictionaries.
            ValueError: If any required statistics for the crowd are missing in `agent_statistics`.
        """

        # Check if the provided databases are dictionaries
        if not isinstance(self.default_database, dict):
            raise ValueError("default_database should be a dictionary.")
        if not isinstance(self.custom_database, dict):
            raise ValueError("custom_database should be a dictionary.")
        if not isinstance(self.agent_statistics, dict):
            raise ValueError("agent_statistics should be a dictionary.")

        # Fill the default database with the ANSURII dataset
        dir_path = Path(__file__).parent.parent.parent.absolute() / "data" / "pkl"
        self.default_database = (fun.load_pickle(dir_path / "ANSUREIIPublic.pkl")).transpose().to_dict()

        # Check if the agent statistics are provided for all parts
        if self.agent_statistics:
            required_parts = {part.name for part in cst.CrowdStat}
            missing_parts = required_parts - self.agent_statistics.keys()
            if missing_parts:
                raise ValueError(f"Missing statistics for the crowd: {', '.join(missing_parts)}")


def draw_agent_part(agent_part: AgentPart, crowd_measures: CrowdMeasures) -> float:
    """
    Draw a random value for the specified agent part from a truncated normal distribution.

    Parameters:
        agent_part (AgentPart): The part of the agent for which to draw a value.
        crowd_measures (CrowdMeasures): An object containing statistical measures of the crowd.

    Returns:
        float: A randomly drawn value for the specified agent part.
    """

    if agent_part == cst.PedestrianParts.sex.name:
        return fun.draw_sex(crowd_measures.agent_statistics[cst.CrowdStat.male_proportion.name])

    mean = crowd_measures.agent_statistics[f"{agent_part}_mean"]
    std_dev = crowd_measures.agent_statistics[f"{agent_part}_std_dev"]
    min_val = crowd_measures.agent_statistics[f"{agent_part}_min"]
    max_val = crowd_measures.agent_statistics[f"{agent_part}_max"]

    return fun.draw_from_trunc_normal(mean, std_dev, min_val, max_val)


def draw_agent_type(crowd_measures: CrowdMeasures) -> cst.AgentTypes:
    """
    Draw a random agent type using tower sampling based on the proportions of
    different agent types in the given crowd measures.

    Parameters:
        crowd_measures (CrowdMeasures): An instance of CrowdMeasures containing
        the statistics of different agent types in the crowd.

    Returns:
        cst.AgentTypes: The randomly selected agent type based on the given
        proportions.

    """

    # Get the proportions of pedestrian and bike agents
    pedestrian_proportion = crowd_measures.agent_statistics[cst.CrowdStat.pedestrian_proportion.name]
    bike_proportion = crowd_measures.agent_statistics[cst.CrowdStat.bike_proportion.name]

    # Check if the proportions sum to 1
    if pedestrian_proportion + bike_proportion != 1.0:
        raise ValueError("The proportions of pedestrian and bike agents should sum to 1.")

    # Draw a random agent type based on the proportions
    cumulative_proportion = 0.0
    random_value = np.random.uniform(0, 1)

    # Loop through the agent types and return the one that corresponds to the random value
    for agent_type in cst.AgentTypes:
        proportion = 0
        if agent_type == cst.AgentTypes.pedestrian:
            proportion = pedestrian_proportion
        elif agent_type == cst.AgentTypes.bike:
            proportion = bike_proportion

        cumulative_proportion += proportion

        if random_value <= cumulative_proportion:
            return agent_type.name

    # If the random value is greater than the sum of proportions, return pedestrian by default
    return cst.AgentTypes.pedestrian.name
