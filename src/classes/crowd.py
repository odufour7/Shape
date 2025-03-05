# TODO : - entrée texte pour donner la base de donnée à partir de laquelle on fait la crowd
# TODO : algo de crowd avec metropolis hastings MCMC où l'énergie, c'est la somme entre coût d'intersection et coût d'aire d'enveloppe convexe

import src.utils.constants as cst
import src.utils.functions as fun
from src.classes.agents import Agent
from src.classes.measures import AgentMeasures, CrowdMeasures
from src.utils.typing_custom import AgentType


class Crowd:
    """Class representing a crowd of pedestrians in a room."""

    def __init__(
        self,
        measures: dict[str, float] | CrowdMeasures = None,
        agents: list[Agent] = None,
    ):
        if isinstance(measures, dict):
            measures = CrowdMeasures(measures)
        elif (measures is not None) and (not isinstance(measures, CrowdMeasures)):
            raise ValueError(
                "`measures` should be an instance of Measures or a dictionary."
            )
        if measures is None:
            measures = CrowdMeasures()  # Create a default CrowdMeasures object

        if agents is None:
            agents = []
        if not isinstance(agents, list) or not all(
            isinstance(agent, Agent) for agent in agents
        ):
            raise ValueError("'agents' should be a list of Agent instances")

        self._measures = measures
        self._agents = agents

    @property
    def agents(self):
        """Get the list of agents in the crowd."""
        return self._agents

    @agents.setter
    def agents(self, value: list[Agent]):
        """Set the agents of the crowd"""
        if not isinstance(value, list) or not all(
            isinstance(agent, Agent) for agent in value
        ):
            raise ValueError("'agents' should be a list of Agent instances")
        if value is None:
            value = []
        self._agents = value

    @property
    def measures(self):
        """Get the measures of the crowd."""
        return self._measures

    @measures.setter
    def measures(self, value: dict[str, float] | CrowdMeasures):
        """Set the measures of the crowd"""
        if isinstance(value, dict):
            value = CrowdMeasures(value)
        elif (value is not None) and (not isinstance(value, CrowdMeasures)):
            raise ValueError(
                "`measures` should be an instance of Measures or a dictionary."
            )
        if value is None:
            value = CrowdMeasures()
        self._measures = value

    def get_number_agents(self) -> int:
        """Get the number of agents in the crowd."""
        return len(self._agents)

    def add_one_agent(self, agent_type: AgentType):
        """
        Adds an agent of the specified type to the crowd.

        Parameters:
        agent_type (AgentType): The type of agent to add. It can be either 'pedestrian' or 'bike'.

        The function initializes the agent's measures based on the agent type and appends the agent to the list of agents.
        For 'pedestrian', the measures include sex, bideltoid breadth, chest depth, and height.
        For 'bike', the measures include wheel width, total length, handlebar length, and top tube length.
        """
        if agent_type == cst.AgentTypes.pedestrian.name:
            # TODO: if crowdpedestrian statistic is empty dictionnary then I draw from the AnsurII database
            agent_measures = AgentMeasures(
                agent_type=cst.AgentTypes.pedestrian.name,
                measures={
                    "sex": fun.draw_agent_part(
                        cst.PedestrianParts.sex.name, self.measures
                    ),
                    "bideltoid_breadth": fun.draw_agent_part(
                        cst.PedestrianParts.bideltoid_breadth.name, self.measures
                    ),
                    "chest_depth": fun.draw_agent_part(
                        cst.PedestrianParts.chest_depth.name, self.measures
                    ),
                    "height": cst.DEFAULT_HEIGHT,
                },
            )
            self.agents.append(Agent(agent_type=agent_type, measures=agent_measures))
        if agent_type == cst.AgentTypes.bike.name:
            agent_measures = AgentMeasures(
                agent_type=cst.AgentTypes.bike.name,
                measures={
                    "wheel_width": fun.draw_agent_part(
                        cst.BikeParts.wheel_width.name, self.measures
                    ),
                    "total_length": fun.draw_agent_part(
                        cst.BikeParts.total_length.name, self.measures
                    ),
                    "handlebar_length": fun.draw_agent_part(
                        cst.BikeParts.handlebar_length.name, self.measures
                    ),
                    "top_tube_length": fun.draw_agent_part(
                        cst.BikeParts.top_tube_length.name, self.measures
                    ),
                },
            )
            self.agents.append(Agent(agent_type=agent_type, measures=agent_measures))


# def remove one agent

# def get_crowd_statistics (number of pedestrians, estimated density, mean, std, min, max of each agent measure quantity)

# def get_crowd_agents_params (list of agents with their measures) to save in json or xml
