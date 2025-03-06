"""This module contains the Measures class to store body measures dynamically based on agent type."""

from dataclasses import dataclass, field
from typing import get_args

import numpy as np

import src.utils.constants as cst
from src.utils import functions as fun
from src.utils.typing_custom import AgentPart, AgentType


@dataclass
class AgentMeasures:
    """Class to store body measures dynamically based on agent type"""

    # équivalent à un constructeur avec un attribut measures de type dict[str, float] initialisé à un dictionnaire vide
    # `field` is imported from the `dataclasses` module and is used to specify default values for dataclass fields.
    # field(default_factory=dict)` ensures that each instance of the class gets its own unique empty dictionary as the default value.
    # avoid mutable (that can be changed) default arguments in Python, as they can lead to unexpected behavior.
    # Ex : e1 = BodyMeasures() e2 = BodyMeasures() e1.measures['bideltoid_breadth'] = 10 print(e2.measures) # ça me retourn {'bideltoid_breadth': 10}

    agent_type: AgentType
    measures: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        """Validates the measures based on the agent type."""
        if self.agent_type not in get_args(AgentType):
            allowed_values = ", ".join(get_args(AgentType))
            raise ValueError(f"Agent type should be one of: {allowed_values}.")
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
        """Return the number of measures stored."""
        return len(self.measures)


@dataclass
class CrowdMeasures:
    """Class to store crowd measures based on agent type"""

    # ANSURII dataset by default (for men and women)
    default_database: dict[int, dict[str, float]] = field(default_factory=dict)
    custom_database: dict[int, dict[str, float]] = field(default_factory=dict)
    agent_statistics: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        """Validates the crowd measures."""
        if not isinstance(self.custom_database, dict):
            raise ValueError("custom_database should be a dictionary.")
        if not isinstance(self.agent_statistics, dict):
            raise ValueError("agent_statistics should be a dictionary.")
        self.default_database = (fun.load_pickle(cst.PICKLE_DIR / "ANSUREIIPublic.pkl")).transpose().to_dict()
        if not isinstance(self.default_database, dict):
            raise ValueError("default_database should be a dictionary.")

        if self.agent_statistics:  # if agent_statistics is not empty
            required_parts = {part.name for part in cst.CrowdStat}
            missing_parts = required_parts - self.agent_statistics.keys()
            if missing_parts:
                raise ValueError(f"Missing statistics for the crowd: {', '.join(missing_parts)}")


def draw_agent_part(agent_part: AgentPart, crowd_measures: CrowdMeasures) -> float:
    """Draw a random value for the specified agent part from a truncated normal distribution."""
    if agent_part == cst.PedestrianParts.sex.name:
        return fun.draw_sex(crowd_measures.agent_statistics[cst.CrowdStat.male_proportion.name])

    mean = crowd_measures.agent_statistics[f"{agent_part}_mean"]
    std_dev = crowd_measures.agent_statistics[f"{agent_part}_std_dev"]
    min_val = crowd_measures.agent_statistics[f"{agent_part}_min"]
    max_val = crowd_measures.agent_statistics[f"{agent_part}_max"]
    return fun.draw_from_trunc_normal(mean, std_dev, min_val, max_val)


def draw_agent_type() -> cst.AgentTypes:
    """Draw a random agent type using tower sampling."""
    cumulative_proportion = 0.0
    random_value = np.random.uniform(0, 1)

    for agent_type in cst.AgentTypes:
        if agent_type == cst.AgentTypes.pedestrian:
            proportion = cst.CrowdStat.pedestrian_proportion.value
        elif agent_type == cst.AgentTypes.bike:
            proportion = cst.CrowdStat.bike_proportion.value
        elif agent_type == cst.AgentTypes.custom:
            proportion = 0
        else:
            # Handle other agent types if needed
            proportion = 0

        cumulative_proportion += proportion

        if random_value <= cumulative_proportion:
            return agent_type

    # If we somehow didn't return earlier (shouldn't happen if proportions sum to 1)
    return cst.AgentTypes.pedestrian
