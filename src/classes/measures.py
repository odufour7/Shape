""" This module contains the Measures class to store body measures dynamically based on agent type. """

from dataclasses import dataclass, field
from typing import get_args

import src.utils.constants as cst
from src.utils.typing_custom import AgentType


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
    agent_type: AgentType
    measures: dict[str, float] = field(default_factory=dict)

    # there should be
    # the wanted statistics of each agent measure quantity (mean, std, min, max)
    # the statistics of the crowd measure quantity :
    #   number of pestestrians,
    #   estimated density
    #
