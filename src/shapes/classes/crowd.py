"""Module containing the Crowd class, which represents a crowd of pedestrians in a room."""

from typing import Optional

import numpy as np
from numpy.typing import NDArray
from shapely.geometry import Point, Polygon

import shapes.utils.constants as cst
from shapes.classes.agents import Agent
from shapes.classes.measures import (
    CrowdMeasures,
    create_bike_measures,
    create_pedestrian_measures,
    draw_agent_measures,
    draw_agent_type,
)
from shapes.utils.typing_custom import ShapeDataType


class Crowd:
    """
    Class representing a crowd of pedestrians in a room.

    Parameters
    ----------
    measures : dict[str, float] | dict[int, dict[str, float]] | CrowdMeasures | None, optional
        Crowd measures data. Can be:
            - A dictionary of agent statistics (str keys, float values)
            - A custom database (int keys, dict values)
            - A CrowdMeasures instance
            - None (default), which creates a default CrowdMeasures object
    agents : list[Agent] | None, optional
        List of Agent instances. If None, an empty list is used.
    boundaries : Polygon | None, optional
        A shapely Polygon instance defining the boundaries.
        If None, a default large square boundary is created.
    """

    def __init__(
        self,
        measures: Optional[dict[str, float] | dict[int, dict[str, float]] | CrowdMeasures | None] = None,
        agents: Optional[list[Agent] | None] = None,
        boundaries: Optional[Polygon | None] = None,
    ) -> None:
        """
        Initialize the class instance with measures, agents, and boundaries.

        Parameters
        ----------
        measures : dict[str, float] | dict[int, dict[str, float]] | CrowdMeasures | None, optional
            Crowd measures data. Can be:
                - A dictionary of agent statistics (str keys, float values)
                - A custom database (int keys, dict values)
                - A CrowdMeasures instance
                - None (default), which creates a default CrowdMeasures object
        agents : list[Agent] | None, optional
            List of Agent instances. If None, an empty list is used.
        boundaries : Polygon | None, optional
            A shapely Polygon instance defining the boundaries.
            If None, a default large square boundary is created.

        Raises
        ------
        ValueError
            If `measures` is not of the expected types.
            If `agents` is not a list of Agent instances.
            If `boundaries` is not a shapely Polygon instance.
        """
        if isinstance(measures, dict) and isinstance(list(measures.keys())[0], int):
            measures = CrowdMeasures(custom_database=measures)
        if isinstance(measures, dict) and isinstance(list(measures.keys())[0], str):
            measures = CrowdMeasures(agent_statistics=measures)
        elif measures is None:
            measures = CrowdMeasures()  # Create a default CrowdMeasures object
        elif not isinstance(measures, CrowdMeasures):
            raise ValueError("`measures` should be an instance of Measures or a dictionary.")

        if agents is None:
            agents = []

        if not isinstance(agents, list) or not all(isinstance(agent, Agent) for agent in agents):
            raise ValueError("'agents' should be a list of Agent instances")

        if boundaries is None:
            boundaries = Polygon(
                [
                    (-(10**6), -(10**6)),
                    (-(10**6), 10**6),
                    (10**6, 10**6),
                    (10**6, -(10**6)),
                ]
            )
        if not isinstance(boundaries, Polygon):
            raise ValueError("'boundaries' should be a shapely Polygon instance")

        self._measures: CrowdMeasures = measures
        self._agents: list[Agent] = agents
        self._boundaries: Polygon = boundaries

    @property
    def agents(self) -> list[Agent]:
        """
        Get the list of agents in the crowd.

        Returns
        -------
        list[Agent]
            A list containing all the agents in the crowd.
        """
        return self._agents

    @agents.setter
    def agents(self, value: list[Agent]) -> None:
        """
        Set the agents of the crowd.

        Parameters
        ----------
        value : list[Agent]
            A list of Agent instances to set as the agents of the crowd.

        Raises
        ------
        ValueError
            If `value` is not a list or if any element in `value` is not an instance of Agent.

        Notes
        -----
        This setter replaces the entire list of agents in the crowd with the provided list.
        """
        if not isinstance(value, list) or not all(isinstance(agent, Agent) for agent in value):
            raise ValueError("'agents' should be a list of Agent instances")
        self._agents = value

    @property
    def measures(self) -> CrowdMeasures:
        """
        Get the measures of the crowd.

        Returns
        -------
        CrowdMeasures
            A CrowdMeasures object containing the measures of the crowd.
        """
        return self._measures

    @measures.setter
    def measures(self, value: Optional[dict[str, float] | dict[int, dict[str, float]] | CrowdMeasures]) -> None:
        """
        Set the measures of the crowd.

        Parameters
        ----------
        value : dict[str, float] | dict[int, dict[str, float]] | CrowdMeasures | None
            The measures to set for the crowd. Can be:
                - A dictionary with string keys and float values (agent statistics)
                - A dictionary with integer keys and dictionary values (custom database)
                - An instance of CrowdMeasures
                - None (creates a new default CrowdMeasures instance)

        Raises
        ------
        ValueError
            If `value` is a dictionary with keys that are neither all integers nor all strings.
            If `value` is neither a dictionary, an instance of CrowdMeasures, nor None.
        """
        if value is None:
            value = CrowdMeasures()
        elif isinstance(value, dict):
            first_key = next(iter(value))
            if isinstance(first_key, int):
                value = CrowdMeasures(custom_database=value)
            elif isinstance(first_key, str):
                value = CrowdMeasures(agent_statistics=value)
            else:
                raise ValueError("Dictionary keys must be either all integers or all strings.")
        elif not isinstance(value, CrowdMeasures):
            raise ValueError("`measures` should be an instance of CrowdMeasures or a dictionary or None.")

        self._measures = value

    @property
    def boundaries(self) -> Polygon:
        """
        Get the boundaries of the room.

        Returns
        -------
        Polygon
            The boundaries of the room as a shapely Polygon object.
        """
        return self._boundaries

    @boundaries.setter
    def boundaries(self, value: Polygon) -> None:
        """
        Set the boundaries of the room.

        Parameters
        ----------
        value : Polygon
            A shapely Polygon instance representing the boundaries of the room.

        Raises
        ------
        ValueError
            If `value` is not an instance of shapely Polygon.
        """
        if not isinstance(value, Polygon):
            raise ValueError("'boundaries' should be a shapely Polygon instance")
        self._boundaries = value

    def get_number_agents(self) -> int:
        """
        Get the number of agents in the crowd.

        Returns
        -------
        int
            The number of agents in the crowd.
        """
        return len(self._agents)

    def add_one_agent(self) -> None:
        """
        Add a new agent to the crowd using available measures data.

        The agent creation follows this priority:
        1. Uses agent statistics if available (when custom database is empty)
        2. Uses custom database if available
        3. Falls back to default ANSURII database if no other data exists
        """
        # Case 1: Use agent statistics if available and custom database is empty
        if self.measures.agent_statistics and not self.measures.custom_database:
            drawn_agent_type = draw_agent_type(self.measures)
            drawn_agent_measures = draw_agent_measures(drawn_agent_type, self.measures)
            self.agents.append(Agent(agent_type=drawn_agent_type, measures=drawn_agent_measures))

        # Case 2: Use the custom database if available
        elif self.measures.custom_database:
            drawn_agent = np.random.choice(np.array(self.measures.custom_database.values(), dtype="object"))

            if drawn_agent["agent_type"] == cst.AgentTypes.pedestrian.name:
                agent_measures = create_pedestrian_measures(drawn_agent)
                self.agents.append(Agent(agent_type=drawn_agent["agent_type"], measures=agent_measures))

            elif drawn_agent["agent_type"] == cst.AgentTypes.bike.name:
                agent_measures = create_bike_measures(drawn_agent)
                self.agents.append(Agent(agent_type=drawn_agent["agent_type"], measures=agent_measures))

        # Case 3: Use the default ANSURII database if no other data is available
        elif not self.measures.agent_statistics and not self.measures.custom_database:
            drawn_agent = np.random.choice(np.array(list(self.measures.default_database.values()), dtype="object"))
            agent_measures = create_pedestrian_measures(drawn_agent)
            self.agents.append(Agent(agent_type=cst.AgentTypes.pedestrian, measures=agent_measures))

    def remove_one_agent(self) -> None:
        """Remove the most recently added agent from the crowd."""
        if self.agents:
            self.agents.pop()

    def create_agents(self, number_agents: int) -> None:
        """
        Create multiple agents in the crowd through repeated additions.

        Parameters
        ----------
        number_agents : int
            Number of agents to create.
        """
        for _ in range(number_agents):
            self.add_one_agent()

    def get_crowd_measures(self) -> dict[str, float]:
        """
        Compute comprehensive statistics for the current crowd composition.

        Returns
        -------
        dict[str, float]
            Dictionary containing aggregated crowd statistics with keys formatted as:
                - "num_{agent_type}": Count of agents per type (e.g., "num_pedestrian")
                - "{part}_mean": Mean value for each body/bike part measurement
                - "{part}_std_dev": Sample standard deviation for each part
                - "{part}_min": Minimum observed value for each part
                - "{part}_max": Maximum observed value for each part
        """
        crowd_measures = {}

        # Loop over the enumeration of AgentTypes to get the number of pedestrians and bikes
        for agent_type in cst.AgentTypes:
            count = sum(1 for agent in self.agents if agent.agent_type == agent_type)
            crowd_measures[f"num_{agent_type.name}"] = float(count)

        # Loop over PedestrianParts and BikeParts to get statistics for each measure
        for parts_enum in [cst.PedestrianParts, cst.BikeParts]:
            for part in parts_enum:
                measures = [agent.measures.__dict__[part.name] for agent in self.agents if hasattr(agent.measures, part.name)]
                if measures:
                    crowd_measures[f"{part.name}_mean"] = float(sum(measures) / len(measures))
                    crowd_measures[f"{part.name}_std_dev"] = float(
                        (sum((x - crowd_measures[f"{part.name}_mean"]) ** 2 for x in measures) / (len(measures) - 1)) ** 0.5
                    )
                    crowd_measures[f"{part.name}_min"] = float(min(measures))
                    crowd_measures[f"{part.name}_max"] = float(max(measures))

        return crowd_measures

    def get_agents_params(self) -> dict[str, dict[str, str | float | ShapeDataType]]:
        """
        Retrieve physical parameters of all agents in a structured format.

        Returns
        -------
        dict[str, dict[str, str | float | ShapeDataType]]
            Dictionary with agent IDs as keys (format: "agent{N}") and values containing:
                agent_type : str
                    Agent classification (e.g., "Pedestrian", "Bike")
                weight (kg) : float
                    Mass of the agent in kilograms
                moi (kg*m^2) : float
                    Moment of inertia in kilogram-square meters
                shapes : ShapeDataType
                    Geometric parameters of the agent's 2D representation
        """
        crowd_dict: dict[str, dict[str, str | float | ShapeDataType]] = {
            f"agent{id_agent}": {
                "agent_type": f"{agent.agent_type.name}",
                "weight_kg": agent.measures.measures[cst.CommonMeasures.weight.name],
                "moi_kgm2": agent.measures.measures["moment_of_inertia"],
                "shapes": agent.shapes2D.get_additional_parameters(),
            }
            for id_agent, agent in enumerate(self.agents)
        }

        return crowd_dict

    def calculate_interpenetration(self) -> float:
        """
        Compute the total interpenetration area between pedestrians and between pedestrians and boundaries.

        Returns
        -------
        float
            The total interpenetration area between pedestrians and between pedestrians and boundaries.
        """
        interpenetration = 0.0
        n_agents = self.get_number_agents()

        # Loop over all agents in the crowd
        for i_agent, current_agent in enumerate(self.agents):
            current_geometric = current_agent.shapes2D.get_geometric_shape()
            # Loop over all other agents in the crowd
            for j in range(i_agent + 1, n_agents):
                neigh_agent = self.agents[j]
                neigh_geometric = neigh_agent.shapes2D.get_geometric_shape()
                # Compute interpenetration between current agent and neighbor
                interpenetration += current_geometric.intersection(neigh_geometric).area
            # Compute interpenetration with the boundaries
            interpenetration += current_geometric.difference(self.boundaries).area

        return interpenetration

    @staticmethod
    def calculate_contact_force(agent_centroid: Point, other_centroid: Point) -> NDArray[np.float64]:
        """
        Compute the repulsive force between two centroids.

        Parameters
        ----------
        agent_centroid : Point
            The centroid of the agent.
        other_centroid : Point
            The centroid of the other agent.

        Returns
        -------
        NDArray[np.float64]
            The normalized direction of the repulsive force as a 1D NumPy array of floats.
            If the centroids coincide, a small random force is returned.
        """
        # Extract coordinates from Shapely Points and convert them to NumPy arrays
        agent_coords = np.array(agent_centroid.coords[0], dtype=np.float64)
        other_coords = np.array(other_centroid.coords[0], dtype=np.float64)

        # Compute the difference vector between centroids
        delta = agent_coords - other_coords

        # Compute the norm (magnitude) of the difference vector
        norm_delta = np.linalg.norm(delta)

        # If the norm is greater than zero, normalize the difference vector
        if norm_delta > 0:
            return delta / norm_delta  # Return normalized direction of the force

        # If centroids coincide, return a small random force as a fallback
        return np.random.rand(2).astype(np.float64)

    @staticmethod
    def calculate_repulsive_force(
        agent_centroid: Point,
        other_centroid: Point,
        repulsion_length: float,
    ) -> NDArray[np.float64]:
        """
        Compute the repulsive force between two centroids, exponentially decreasing with distance.

        Parameters
        ----------
        agent_centroid : Point
            The centroid of the agent.
        other_centroid : Point
            The centroid of the other agent.
        repulsion_length : float
            Coefficient used to compute the magnitude of the repulsive force between agents.
            The force decreases exponentially with distance divided by this repulsion_length.

        Returns
        -------
        NDArray[np.float64]
            A 1D NumPy array representing the repulsive force vector.
            If the centroids coincide, a small random force is returned.
        """
        # Extract coordinates from Shapely Points and convert them to NumPy arrays
        agent_coords = np.array(agent_centroid.coords[0], dtype=np.float64)
        other_coords = np.array(other_centroid.coords[0], dtype=np.float64)

        # Compute the difference vector between centroids
        delta = agent_coords - other_coords

        # Compute the norm (magnitude) of the difference vector
        norm_delta = np.linalg.norm(delta)

        # Handle edge case where centroids coincide (norm_delta == 0)
        if norm_delta == 0:
            return np.random.rand(2).astype(np.float64)  # Small random force as fallback

        # Normalize the difference vector to get the direction of the force
        direction = delta / norm_delta

        # Compute the magnitude of the repulsive force (exponentially decreasing with distance)
        force_magnitude = np.exp(-norm_delta / repulsion_length)

        # Return the repulsive force vector as a NumPy array
        return np.array(force_magnitude * direction)

    @staticmethod
    def calculate_rotational_force() -> float:
        """
        Generate a random rotational force value.

        Returns
        -------
        float
            Random rotational force in degrees between -10.0° and 10.0°.
        """
        return np.random.uniform(-10.0, 10.0)

    def pack_agents_with_forces(self, wall_interaction: bool, repulsion_length: float) -> None:
        """
        Simulate crowd dynamics by applying physics-based forces between agents.

        Performs iterative force calculations to separate overlapping agents while
        maintaining boundary constraints. Implements a cooling system to gradually
        reduce movement intensity.

        Parameters
        ----------
        wall_interaction : bool
            If True, includes interactions between agents and walls in the simulation.
            If False, wall interactions are ignored.
        repulsion_length : float
            Coefficient used to compute the magnitude of the repulsive force between agents.
            The force decreases exponentially with distance divided by this repulsion_length.

        Notes
        -----
        The walls are assumed to be boundaries, they are therefore not considered as obstacles.
        The walls can be any Polygon object.
        """
        Temperature = 1.0
        for _ in range(cst.MAX_NB_ITERATIONS):
            # Check for overlaps and apply forces if necessary
            for i_agent, current_agent in enumerate(self.agents):
                force: NDArray[np.float64] = np.array([0.0, 0.0])  # in centimeters
                rotational_force: float = 0.0  # in degrees
                current_geometric = current_agent.shapes2D.get_geometric_shape()
                current_centroid: Point = current_geometric.centroid

                # Compute repulsive force between agents
                for j_agent, neigh_agent in enumerate(self.agents):
                    neigh_geometric = neigh_agent.shapes2D.get_geometric_shape()
                    if i_agent != j_agent:
                        neigh_centroid: Point = neigh_geometric.centroid
                        force += Crowd.calculate_repulsive_force(current_centroid, neigh_centroid, repulsion_length)
                        if current_geometric.intersects(neigh_geometric):
                            force += Crowd.calculate_contact_force(current_centroid, neigh_centroid)
                            rotational_force += Crowd.calculate_rotational_force() * Temperature

                if wall_interaction:
                    # Compute repulsive force between agent and wall
                    if not self.boundaries.contains(current_geometric):
                        # Compute the nearest point on the agent between the agent and the boundary
                        nearest_point = Point(
                            self.boundaries.exterior.interpolate(
                                self.boundaries.exterior.project(
                                    current_geometric.centroid
                                )  # Compute projection distance along boundary
                            ).coords[0]
                        )
                        force += Crowd.calculate_contact_force(current_centroid, nearest_point)
                        rotational_force += Crowd.calculate_rotational_force() * Temperature

                # Rotate pedestrian
                current_agent.rotate(rotational_force)

                # Translate pedestrian
                if np.linalg.norm(force) > 0:
                    new_position = Point(np.array(current_centroid.coords[0], dtype=np.float64) + force)
                    if self.boundaries.contains(new_position):
                        current_agent.translate(force[0], force[1])

            # Decrease the temperature at each iteration
            Temperature -= 0.1
            Temperature = max(0.0, Temperature)

    def unpack_crowd(self) -> None:
        """Translate all agents in the crowd to the origin (0, 0)."""
        for agent in self.agents:
            current_position: Point = agent.get_position()
            translation_vector = np.array([-current_position.x, -current_position.y])
            agent.translate(*translation_vector)
