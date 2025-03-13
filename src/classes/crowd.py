"""Module containing the Crowd class, which represents a crowd of pedestrians in a room."""

from typing import Optional

import numpy as np
from numpy.typing import NDArray
from scipy.spatial import ConvexHull  # pylint: disable=import-error
from shapely.geometry import Point, Polygon

import src.utils.constants as cst
from src.classes.agents import Agent
from src.classes.measures import (
    CrowdMeasures,
    create_bike_measures,
    create_pedestrian_measures,
    draw_agent_measures,
    draw_agent_type,
)
from src.utils.typing_custom import ShapeDataType


class Crowd:
    """Class representing a crowd of pedestrians in a room."""

    def __init__(
        self,
        measures: Optional[dict[str, float] | dict[int, dict[str, float]] | CrowdMeasures | None] = None,
        agents: Optional[list[Agent] | None] = None,
        boundaries: Optional[Polygon | None] = None,
    ):
        if isinstance(measures, dict) and isinstance(list(measures.keys())[0], int):
            measures = CrowdMeasures(custom_database=measures)  # type: ignore[arg-type]
        if isinstance(measures, dict) and isinstance(list(measures.keys())[0], str):
            measures = CrowdMeasures(agent_statistics=measures)  # type: ignore[arg-type]
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
        """Get the list of agents in the crowd.

        Parameters
        ----------
            None

        Returns
        -------
            list[Agent]: A list containing all the agents in the crowd.

        """
        return self._agents

    @agents.setter
    def agents(self, value: list[Agent]) -> None:
        """Set the agents of the crowd.

        Parameters
        ----------
            value (list[Agent]): A list of Agent instances to set as the agents of the crowd.

        Returns
        -------
            None

        Raises
        ------
            ValueError: If 'value' is not a list or if any element in 'value' is not an instance of Agent.

        """
        if not isinstance(value, list) or not all(isinstance(agent, Agent) for agent in value):
            raise ValueError("'agents' should be a list of Agent instances")
        self._agents = value

    @property
    def measures(self) -> CrowdMeasures:
        """Get the measures of the crowd.

        Parameters
        ----------
            None

        Returns
        -------
            dict[str, float] | CrowdMeasures: A dictionary or CrowdMeasures object containing the measures of the crowd.

        """
        return self._measures

    @measures.setter
    def measures(self, value: Optional[dict[str, float] | dict[int, dict[str, float]] | CrowdMeasures]) -> None:
        """Set the measures of the crowd.

        Parameters
        ----------
        value : dict[str, float] | dict[int, dict[str, float]] | CrowdMeasures | None
            The measures to set for the crowd. It can be either a dictionary
            with string keys and float values, a dictionary with integer keys and dictionary values,
            an instance of CrowdMeasures, or None.

        Raises
        ------
        ValueError
            If the provided value is neither a dictionary nor an instance of CrowdMeasures nor None.

        Notes
        -----
        If the provided value is a dictionary, it will be converted to a CrowdMeasures instance.
        If the provided value is None, a new CrowdMeasures instance will be created and assigned.

        """
        if value is None:
            value = CrowdMeasures()
        elif isinstance(value, dict):
            first_key = next(iter(value))
            if isinstance(first_key, int):
                value = CrowdMeasures(custom_database=value)  # type: ignore[arg-type]
            elif isinstance(first_key, str):
                value = CrowdMeasures(agent_statistics=value)  # type: ignore[arg-type]
            else:
                raise ValueError("Dictionary keys must be either all integers or all strings.")
        elif not isinstance(value, CrowdMeasures):
            raise ValueError("`measures` should be an instance of CrowdMeasures or a dictionary or None.")

        self._measures = value

    @property
    def boundaries(self) -> Polygon:
        """Get the boundaries of the room.

        Parameters
        ----------
            None

        Returns
        -------
            Polygon: The boundaries of the room as a Polygon object.

        """
        return self._boundaries

    @boundaries.setter
    def boundaries(self, value: Polygon) -> None:
        """Set the boundaries of the room.

        Parameters
        ----------
            value (Polygon): A shapely Polygon instance representing the boundaries of the room.

        Raises
        ------
            ValueError: If 'value' is not an instance of shapely Polygon.

        """
        if not isinstance(value, Polygon):
            raise ValueError("'boundaries' should be a shapely Polygon instance")
        self._boundaries = value

    def get_number_agents(self) -> int:
        """Get the number of agents in the crowd.

        Parameters
        ----------
            None

        Returns
        -------
            int: The number of agents in the crowd.

        """
        return len(self._agents)

    def add_one_agent(self) -> None:
        """Add an agent of the specified type to the crowd."""
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
            drawn_agent = np.random.choice(np.array(self.measures.default_database.values(), dtype="object"))
            agent_measures = create_pedestrian_measures(drawn_agent)
            self.agents.append(Agent(agent_type=cst.AgentTypes.pedestrian, measures=agent_measures))

    def remove_one_agent(self) -> None:
        """Remove one agent from the crowd.

        This method removes the last agent from the list of agents if the list is not empty.

        """
        if self.agents:
            self.agents.pop()

    def create_agents(self, number_agents: float) -> None:
        """Create a specified number of agents in the crowd.

        Parameters
        ----------
        number_agents : float
            The number of agents to create. This will be converted to an integer.

        """
        for _ in range(int(number_agents)):
            self.add_one_agent()

    def get_crowd_measures(self) -> dict[str, float] | dict[int, dict[str, float]] | CrowdMeasures:
        """Calculate and return crowd statistics.

        This method computes various statistics for the crowd, including the number of agents of each type
        and statistical measures (mean, standard deviation, minimum, and maximum) for different attributes
        of the agents.

        Returns
        -------
        dict[str, float]
            A dictionary containing the crowd statistics. The keys include:
            - "num_<AgentType>": Number of agents for each type (e.g., "num_Pedestrian", "num_Bike").
            - "<Attribute>_mean": Mean value of the attribute across all agents.
            - "<Attribute>_std_dev": Standard deviation of the attribute across all agents.
            - "<Attribute>_min": Minimum value of the attribute across all agents.
            - "<Attribute>_max": Maximum value of the attribute across all agents.

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

    def get_agents_params(self) -> dict[str, dict[str, str | ShapeDataType]]:
        """Retrieve the parameters of each agent in the crowd.

        Returns
        -------
        list[dict[str, float]]
            A list of dictionaries, where each dictionary represents the parameters of a single agent.
            Each dictionary contains the following keys:
            - "agent_type" : str
                The type of the agent (e.g., "Pedestrian", "Bike").
            - "shapes" : dict[str, float]
                Additional parameters related to the agent's shapes.

        """
        crowd_dict: dict[str, dict[str, str | ShapeDataType]] = {
            f"agent{id_agent}": {
                "agent_type": f"{agent.agent_type.name}",
                "shapes": agent.shapes2D.get_additional_parameters(),
            }
            for id_agent, agent in enumerate(self.agents)
        }

        return crowd_dict

    def calculate_interpenetration(self, with_inflation: bool = False) -> float:
        """Calculate the total interpenetration area between pedestrians.

        This method computes the total area of interpenetration between the geometric shapes of pedestrians
        in the crowd. Optionally, the geometric shapes can be inflated by a buffer before performing the calculation.

        Parameters
        ----------
        with_inflation : bool, optional
            If True, inflates the geometric shapes by a buffer of 5.0 units before calculating the interpenetration.
            Default is False.

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
            # Inflate the geometric shape if required
            if with_inflation:
                current_geometric = current_geometric.buffer(5.0)
            # Loop over all other agents in the crowd
            for j in range(i_agent + 1, n_agents):
                neigh_agent = self.agents[j]
                neigh_geometric = neigh_agent.shapes2D.get_geometric_shape()
                # Inflate the geometric shape if required
                if with_inflation:
                    neigh_geometric = neigh_geometric.buffer(5.0)
                # Calculate interpenetration between current agent and neighbor
                interpenetration += current_geometric.intersection(neigh_geometric).area
            # Calculate interpenetration with the boundaries
            interpenetration += current_geometric.difference(self.boundaries).area

        return interpenetration

    def compute_crowd_convex_hull_area(self) -> float:
        """Calculate the convex hull area of the crowd.

        This method computes the area of the convex hull that encloses all agents in the crowd. It collects
        the exterior coordinates of the 2D shapes of all agents, determines the convex hull of these points,
        and calculates its area.

        Returns
        -------
        float
            The area of the convex hull enclosing the crowd.

        """
        points = []
        for agent in self.agents:
            points.extend(agent.shapes2D.get_geometric_shape().exterior.coords[:-1])
        hull = ConvexHull(points)

        return float(hull.area)

    def compute_energy(self) -> float:
        """Compute the energy of the crowd.

        The energy is calculated as a weighted sum of the interpenetration and the convex hull area of the crowd.
        The interpenetration is scaled by a factor of 100, and the convex hull area is scaled by a factor of 0.1.

        Returns
        -------
            float: The computed energy of the crowd.

        """
        interpenetration = self.calculate_interpenetration(with_inflation=True)
        convex_hull_area = self.compute_crowd_convex_hull_area()

        return 100.0 * interpenetration + convex_hull_area / 10.0

    def pack_agents_MCMC(self) -> float:
        """Run an MCMC algorithm to pack the agents of the crowd.

        This method iteratively attempts to move and rotate agents in the crowd
        to minimize the overall energy of the system. It uses a Monte Carlo
        Markov Chain (MCMC) approach to explore the state space of possible
        configurations.

        Returns
        -------
            float: The final energy of the system after attempting to pack the agents.

        """
        current_energy = self.compute_energy()
        cpt_rejected = 0

        # Perform a number of iterations to pack the agents
        for _ in range(cst.MAX_NB_ITERATIONS):
            # Choose a random agent
            if self.agents is None:
                raise ValueError("No agents in the crowd")
            agent = np.random.choice(np.array(self.agents, dtype="object"))

            # Perform random move
            dtheta = np.random.uniform(-cst.MAX_ROTATION, cst.MAX_ROTATION)
            dx, dy = (
                np.random.uniform(-cst.MAX_MOVE_X, cst.MAX_MOVE_X),
                np.random.uniform(-cst.MAX_MOVE_Y, cst.MAX_MOVE_Y),
            )
            agent.rotate(dtheta)
            agent.translate(dx, dy)

            # Calculate new energy
            new_energy = self.compute_energy()
            delta_energy = new_energy - current_energy

            # Accept or reject the move based on the energy difference
            if delta_energy < 0.0:
                current_energy = new_energy
            else:
                cpt_rejected += 1
                agent.rotate(-dtheta)
                agent.translate(-dx, -dy)

        return current_energy

    @staticmethod
    def calculate_contact_force(agent_centroid: Point, other_centroid: Point) -> NDArray[np.float64]:
        """
        Calculate the repulsive force between two centroids.

        Parameters
        ----------
        agent_centroid : Point
            The centroid of the agent (Shapely Point object).
        other_centroid : Point
            The centroid of the other agent (Shapely Point object).

        Returns
        -------
        NDArray[np.float64]
            The normalized direction of the repulsive force as a 1D NumPy array of floats.
            If the centroids coincide, a small random force is returned.
        """
        # Extract coordinates from Shapely Points and convert them to NumPy arrays
        agent_coords = np.array(agent_centroid.coords[0], dtype=np.float64)
        other_coords = np.array(other_centroid.coords[0], dtype=np.float64)

        # Calculate the difference vector between centroids
        delta = agent_coords - other_coords

        # Compute the norm (magnitude) of the difference vector
        norm_delta = np.linalg.norm(delta)

        # If the norm is greater than zero, normalize the difference vector
        if norm_delta > 0:
            return delta / norm_delta  # Return normalized direction of the force

        # If centroids coincide, return a small random force as a fallback
        return np.random.rand(2).astype(np.float64)

    # the repulsive force should exponentially decrease with the distance between the two agents
    # @staticmethod
    # def calculate_repulsive_force(agent_centroid: Point, other_centroid: Point) -> NDArray[np.float64]:
    #     """Calculate the repulsive force between two centroids, exponentially decreasing with distance."""
    #     delta = agent_centroid - other_centroid
    #     norm_delta = np.linalg.norm(delta)
    #     if norm_delta == 0:
    #         return np.random.rand(2)  # Small random force if centroids coincide
    #     direction = delta / norm_delta  # direction of the force
    #     # Calculate the magnitude of the repulsive force, exponentially decreasing with distance
    #     force_magnitude = np.exp(-cst.DEFAULT_DECAY_REPULSION_RATE * norm_delta)
    #     # TODO : voir comment on peut modifier ce decay depuis streamlit
    #     # Return the repulsive force vector
    #     return np.array(force_magnitude * direction)
    @staticmethod
    def calculate_repulsive_force(agent_centroid: Point, other_centroid: Point) -> NDArray[np.float64]:
        """
        Calculate the repulsive force between two centroids, exponentially decreasing with distance.

        Parameters
        ----------
        agent_centroid : Point
            The centroid of the agent (Shapely Point object).
        other_centroid : Point
            The centroid of the other agent (Shapely Point object).

        Returns
        -------
        NDArray[np.float64]
            A 1D NumPy array representing the repulsive force vector.
            If the centroids coincide, a small random force is returned.
        """
        # Extract coordinates from Shapely Points and convert them to NumPy arrays
        agent_coords = np.array(agent_centroid.coords[0], dtype=np.float64)
        other_coords = np.array(other_centroid.coords[0], dtype=np.float64)

        # Calculate the difference vector between centroids
        delta = agent_coords - other_coords

        # Compute the norm (magnitude) of the difference vector
        norm_delta = np.linalg.norm(delta)

        # Handle edge case where centroids coincide (norm_delta == 0)
        if norm_delta == 0:
            return np.random.rand(2).astype(np.float64)  # Small random force as fallback

        # Normalize the difference vector to get the direction of the force
        direction = delta / norm_delta

        # Calculate the magnitude of the repulsive force (exponentially decreasing with distance)
        force_magnitude = np.exp(-cst.DEFAULT_DECAY_REPULSION_RATE * norm_delta)

        # Return the repulsive force vector as a NumPy array
        return np.array(force_magnitude * direction)

    @staticmethod
    def calculate_rotational_force() -> float:
        """Calculate a rotational force based on the agent's current orientation."""
        return np.random.uniform(-10.0, 10.0)  # Random rotational force between -10 and 10 degrees

    # TODO : améliroer la rapidité
    def pack_agents_with_forces(self) -> None:
        """Simulate the application of forces on agents within a polygonal cell over a number of iterations."""
        Temperature = 1.0
        for _ in range(cst.MAX_NB_ITERATIONS):
            # Check for overlaps and apply forces if necessary
            for i_agent, current_agent in enumerate(self.agents):
                force = np.array([0.0, 0.0])
                rotational_force = 0.0
                current_geometric = current_agent.shapes2D.get_geometric_shape()
                current_centroid: Point = current_geometric.centroid
                # Calculate repulsive force between agents
                for j_agent, neigh_agent in enumerate(self.agents):
                    neigh_geometric = neigh_agent.shapes2D.get_geometric_shape()
                    if i_agent != j_agent:
                        neigh_centroid: Point = neigh_geometric.centroid
                        force += Crowd.calculate_repulsive_force(current_centroid, neigh_centroid)
                        if current_geometric.intersects(neigh_geometric):
                            force += Crowd.calculate_contact_force(current_centroid, neigh_centroid)
                            rotational_force += Crowd.calculate_rotational_force() * Temperature

                # TODO : add a possibility to remove wall interaction
                # Calculate repulsive force between agent and wall
                # if not self.boundaries.contains(current_geometric):
                #     nearest_point = np.array(
                #         self.boundaries.exterior.interpolate(self.boundaries.exterior.project(current_geometric.centroid)).
                #              coords[0
                #         ]
                #     )
                #     force += Crowd.calculate_contact_force(current_centroid, nearest_point)
                current_agent.rotate(rotational_force)
                # Apply force to agent position if non-zero and within bounds
                if np.linalg.norm(force) > 0:
                    new_position = current_centroid + force
                    if self.boundaries.contains(Point(new_position)):
                        current_agent.translate(force[0], force[1])
            Temperature -= 0.1  # Decrease the temperature at each iteration
            Temperature = max(0.0, Temperature)
