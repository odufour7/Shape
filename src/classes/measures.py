"""Module containing the Measures class to store body measures dynamically based on agent type."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

import numpy as np

import src.utils.constants as cst
from src.utils import functions as fun
from src.utils.typing_custom import Sex


@dataclass
class AgentMeasures:
    """Class to store body measures dynamically based on agent type."""

    agent_type: cst.AgentTypes
    measures: dict[str, float | Sex] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the measures based on the agent type after the object is initialized.

        Raises
        ------
            ValueError: If the agent type is not one of the allowed values.
            ValueError: If measures is not a dictionary.
            ValueError: If required measures for the agent type are missing.
            ValueError: If extra measures are provided for non-custom agent types.

        Validations performed
        ---------------------
            - Checks if the agent type is valid.
            - Ensures measures is a dictionary.
            - Determines required parts based on the agent type.
            - Validates that all required measures are present.
            - Validates that no extra measures are provided for non-custom agent types.

        """
        # Check if the agent type is valid
        if not isinstance(self.agent_type, cst.AgentTypes):
            raise ValueError(f"Agent type should be one of: {[member.name for member in cst.AgentTypes]}.")

        # Check if measures is a dictionary
        if not isinstance(self.measures, dict):
            raise ValueError("measures should be a dictionary.")

        # Determine required parts based on the agent type
        if self.agent_type == cst.AgentTypes.pedestrian:
            required_parts = {part.name for part in cst.PedestrianParts}
        elif self.agent_type == cst.AgentTypes.bike:
            required_parts = {part.name for part in cst.BikeParts}
        elif self.agent_type == cst.AgentTypes.custom:
            required_parts = set()  # Custom agents have no predefined required parts
        else:
            raise ValueError(f"Unknown agent type: {self.agent_type}")

        # Validate that all required measures are present
        missing_parts = required_parts - self.measures.keys()
        if missing_parts:
            raise ValueError(f"Missing measures for {self.agent_type}: {', '.join(missing_parts)}")

        # Validate that no extra measures are provided
        extra_parts = self.measures.keys() - required_parts
        if extra_parts and self.agent_type != cst.AgentTypes.custom:
            raise ValueError(f"Extra measures provided for {self.agent_type}: {', '.join(extra_parts)}")

    def number_of_measures(self) -> int:
        """Return the number of measures stored.

        Returns
        -------
        int
            The number of measures stored in the 'measures' attribute.

        """
        return len(self.measures)


@dataclass
class CrowdMeasures:
    """Class to store crowd measures based on agent type."""

    # ANSURII dataset by default (for men and women)
    default_database: dict[int, dict[str, float]] = field(default_factory=dict)
    custom_database: dict[int, dict[str, float]] = field(default_factory=dict)
    agent_statistics: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the crowd measures after the dataclass initialization.

        This method performs the following validations and operations:
        1. Ensures that `default_database`, `custom_database`, and `agent_statistics` are dictionaries.
        2. Loads the ANSURII dataset into the `default_database` from a pickle file located in the data directory.
        3. Checks if the `agent_statistics` dictionary contains statistics for all required parts of the crowd.
           Raises a ValueError if any required statistics are missing.

        Raises
        ------
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


def draw_agent_measures(agent_type: cst.AgentTypes, crowd_measures: CrowdMeasures) -> AgentMeasures:
    """Draw a random set of agent measures based on the agent type."""
    if agent_type == cst.AgentTypes.pedestrian:
        return _draw_pedestrian_measures(crowd_measures)
    if agent_type == cst.AgentTypes.bike:
        return _draw_bike_measures(crowd_measures)
    raise ValueError(f"Invalid agent type '{agent_type}'. Please provide a valid agent type.")


def _draw_pedestrian_measures(crowd_measures: CrowdMeasures) -> AgentMeasures:
    """Draw pedestrian-specific measures."""
    agent_sex = fun.draw_sex(crowd_measures.agent_statistics[cst.CrowdStat.male_proportion.name])
    measures = {
        "sex": agent_sex,
        "bideltoid_breadth": _draw_measure(crowd_measures, agent_sex, cst.PedestrianParts.bideltoid_breadth),
        "chest_depth": _draw_measure(crowd_measures, agent_sex, cst.PedestrianParts.chest_depth),
        "height": cst.DEFAULT_HEIGHT,
    }
    return AgentMeasures(agent_type=cst.AgentTypes.pedestrian, measures=measures)


def _draw_bike_measures(crowd_measures: CrowdMeasures) -> AgentMeasures:
    """Draw bike-specific measures."""
    measures: Mapping[str, float | Sex] = {
        cst.BikeParts.wheel_width.name: _draw_measure(crowd_measures, None, cst.BikeParts.wheel_width),
        cst.BikeParts.total_length.name: _draw_measure(crowd_measures, None, cst.BikeParts.total_length),
        cst.BikeParts.handlebar_length.name: _draw_measure(crowd_measures, None, cst.BikeParts.handlebar_length),
        cst.BikeParts.top_tube_length.name: _draw_measure(crowd_measures, None, cst.BikeParts.top_tube_length),
    }

    return AgentMeasures(agent_type=cst.AgentTypes.bike, measures=dict(measures))


def _draw_measure(crowd_measures: CrowdMeasures, sex: str | None, part_enum: cst.PedestrianParts | cst.BikeParts) -> float:
    """Draw a measure from truncated normal distribution."""
    prefix = f"{sex}_" if sex else ""
    stats = crowd_measures.agent_statistics

    mean = stats[f"{prefix}{part_enum.name}_mean"]
    std_dev = stats[f"{prefix}{part_enum.name}_std_dev"]
    min_val = stats[f"{prefix}{part_enum.name}_min_val"]
    max_val = stats[f"{prefix}{part_enum.name}_max_val"]

    return fun.draw_from_trunc_normal(mean, std_dev, min_val, max_val)


def draw_agent_type(crowd_measures: CrowdMeasures) -> cst.AgentTypes:
    """Draw a random agent type using tower sampling.

    Parameters
    ----------
    crowd_measures : CrowdMeasures
        An instance of CrowdMeasures containing the statistics of different agent types in the crowd.

    Returns
    -------
    cst.AgentTypes
        The randomly selected agent type based on the given proportions.

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
        proportion = 0.0
        if agent_type == cst.AgentTypes.pedestrian:
            proportion = pedestrian_proportion
        elif agent_type == cst.AgentTypes.bike:
            proportion = bike_proportion

        cumulative_proportion += proportion

        if random_value <= cumulative_proportion:
            return agent_type

    # If the random value is greater than the sum of proportions, return pedestrian by default
    return cst.AgentTypes.pedestrian


def create_pedestrian_measures(agent_data: dict[str, float]) -> AgentMeasures:
    """Create pedestrian-specific agent measures."""
    return AgentMeasures(
        agent_type=cst.AgentTypes.pedestrian,
        measures={
            "sex": agent_data["sex"],
            "bideltoid_breadth": agent_data["bideltoid breadth [cm]"],
            "chest_depth": agent_data["chest depth [cm]"],
            "height": agent_data["height [cm]"],
        },
    )


def create_bike_measures(agent_data: dict[str, float]) -> AgentMeasures:
    """Create bike-specific agent measures."""
    return AgentMeasures(
        agent_type=cst.AgentTypes.bike,
        measures={
            "wheel_width": agent_data["wheel width [cm]"],
            "total_length": agent_data["total length [cm]"],
            "handlebar_length": agent_data["handlebar length [cm]"],
            "top_tube_length": agent_data["top tube length [cm]"],
        },
    )
