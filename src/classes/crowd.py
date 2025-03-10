"""This module contains the Crowd class, which represents a crowd of pedestrians in a room."""

import numpy as np
from scipy.spatial import ConvexHull
from shapely.geometry import Point, Polygon

import src.utils.constants as cst
from src.classes.agents import Agent
from src.classes.measures import AgentMeasures, CrowdMeasures, draw_agent_part, draw_agent_type


class Crowd:
    """Class representing a crowd of pedestrians in a room."""

    def __init__(
        self,
        measures: dict[str, float] | CrowdMeasures = None,
        agents: list[Agent] = None,
        boundaries: Polygon = None,
    ):
        if isinstance(measures, dict):
            measures = CrowdMeasures(measures)
        elif measures is None:
            measures = CrowdMeasures()  # Create a default CrowdMeasures object
        elif (measures is not None) and (not isinstance(measures, CrowdMeasures)):
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

        self._measures = measures
        self._agents = agents
        self._boundaries = boundaries

    @property
    def agents(self) -> list[Agent]:
        """
        Get the list of agents in the crowd.

        Returns:
            list[Agent]: A list containing all the agents in the crowd.
        """

        return self._agents

    @agents.setter
    def agents(self, value: list[Agent]) -> None:
        """
        Set the agents of the crowd.

        Args:
            value (list[Agent]): A list of Agent instances to set as the agents of the crowd.

        Raises:
            ValueError: If 'value' is not a list or if any element in 'value' is not an instance of Agent.
        """

        if not isinstance(value, list) or not all(isinstance(agent, Agent) for agent in value):
            raise ValueError("'agents' should be a list of Agent instances")
        if value is None:
            value = []
        self._agents = value

    @property
    def measures(self) -> dict[str, float] | CrowdMeasures:
        """
        Get the measures of the crowd.

        Returns:
            dict[str, float] | CrowdMeasures: A dictionary or CrowdMeasures object containing the measures of the crowd.
        """

        return self._measures

    @measures.setter
    def measures(self, value: dict[str, float] | CrowdMeasures) -> None:
        """
        Set the measures of the crowd.

        Parameters
        ----------
        value : dict[str, float] or CrowdMeasures
            The measures to set for the crowd. It can be either a dictionary
            with string keys and float values or an instance of CrowdMeasures.

        Raises
        ------
        ValueError
            If the provided value is neither a dictionary nor an instance of CrowdMeasures.

        Notes
        -----
        If the provided value is a dictionary, it will be converted to a CrowdMeasures instance.
        If the provided value is None, a new CrowdMeasures instance will be created and assigned.
        """
        if isinstance(value, dict):
            value = CrowdMeasures(value)
        elif (value is not None) and (not isinstance(value, CrowdMeasures)):
            raise ValueError("`measures` should be an instance of Measures or a dictionary.")
        if value is None:
            value = CrowdMeasures()
        self._measures = value

    @property
    def boundaries(self) -> Polygon:
        """
        Get the boundaries of the room.

        Returns:
            Polygon: The boundaries of the room as a Polygon object.
        """

        return self._boundaries

    @boundaries.setter
    def boundaries(self, value: Polygon) -> None:
        """
        Set the boundaries of the room.

        Parameters:
            value (Polygon): A shapely Polygon instance representing the boundaries of the room.

        Raises:
            ValueError: If 'value' is not an instance of shapely Polygon.
        """

        if not isinstance(value, Polygon):
            raise ValueError("'boundaries' should be a shapely Polygon instance")
        self._boundaries = value

    def get_number_agents(self) -> int:
        """
        Get the number of agents in the crowd.

        Returns:
            int: The number of agents in the crowd.
        """

        return len(self._agents)

    def add_one_agent(self) -> None:
        """Adds an agent of the specified type to the crowd."""
        # if the agent statistics are available, draw an agent from the statistics
        if len(self.measures.agent_statistics) > 0 and len(self.measures.custom_database) == 0:
            drawn_agent_type = draw_agent_type(self.measures)
            if drawn_agent_type == cst.AgentTypes.pedestrian.name:
                draw_sex = draw_agent_part(cst.PedestrianParts.sex.name, self.measures)
                agent_measures = AgentMeasures(
                    agent_type=cst.AgentTypes.pedestrian.name,
                    measures={
                        "sex": draw_sex,
                        "bideltoid_breadth": draw_agent_part(
                            f"{draw_sex}_{cst.PedestrianParts.bideltoid_breadth.name}", self.measures
                        ),
                        "chest_depth": draw_agent_part(f"{draw_sex}_{cst.PedestrianParts.chest_depth.name}", self.measures),
                        "height": cst.DEFAULT_HEIGHT,
                    },
                )
                self.agents.append(Agent(agent_type=drawn_agent_type, measures=agent_measures))
            elif drawn_agent_type == cst.AgentTypes.bike.name:
                agent_measures = AgentMeasures(
                    agent_type=cst.AgentTypes.bike.name,
                    measures={
                        "wheel_width": draw_agent_part(cst.BikeParts.wheel_width.name, self.measures),
                        "total_length": draw_agent_part(cst.BikeParts.total_length.name, self.measures),
                        "handlebar_length": draw_agent_part(cst.BikeParts.handlebar_length.name, self.measures),
                        "top_tube_length": draw_agent_part(cst.BikeParts.top_tube_length.name, self.measures),
                    },
                )
                self.agents.append(Agent(agent_type=drawn_agent_type, measures=agent_measures))
        # if the custom database is available, draw an agent from the custom database
        elif self.measures.custom_database and not self.measures.agent_statistics:
            # Draw an agent from the custom database
            drawn_agent = np.random.choice(list(self.measures.custom_database.values()))
            # TODO: selon le type de fichier en entrée, le draw agent devra être adapté pour les mensurations
            if drawn_agent["agent_type"] == cst.AgentTypes.pedestrian.name:
                agent_measures = AgentMeasures(
                    agent_type=cst.AgentTypes.pedestrian.name,
                    measures={
                        "sex": drawn_agent["sex"],
                        "bideltoid_breadth": drawn_agent["bideltoid breadth [cm]"],
                        "chest_depth": drawn_agent["chest depth [cm]"],
                        "height": drawn_agent["height [cm]"],
                    },
                )
                self.agents.append(Agent(agent_type=drawn_agent["agent_type"], measures=agent_measures))
            elif drawn_agent["agent_type"] == cst.AgentTypes.bike.name:
                agent_measures = AgentMeasures(
                    agent_type=cst.AgentTypes.bike.name,
                    measures={
                        "wheel_width": drawn_agent["wheel width [cm]"],
                        "total_length": drawn_agent["total length [cm]"],
                        "handlebar_length": drawn_agent["handlebar length [cm]"],
                        "top_tube_length": drawn_agent["top tube length [cm]"],
                    },
                )
                self.agents.append(Agent(agent_type=drawn_agent["agent_type"], measures=agent_measures))
        # if the custom database and agent statistics are not available, draw an agent from the default ANSURII database
        elif not self.measures.custom_database and not self.measures.agent_statistics:
            # draw an angent from the default ANSURII database
            drawn_agent = np.random.choice(list(self.measures.default_database.values()))
            agent_measures = AgentMeasures(
                agent_type=cst.AgentTypes.pedestrian.name,
                measures={
                    "sex": drawn_agent["sex"],
                    "bideltoid_breadth": drawn_agent["bideltoid breadth [cm]"],
                    "chest_depth": drawn_agent["chest depth [cm]"],
                    "height": drawn_agent["height [cm]"],
                },
            )
            self.agents.append(Agent(agent_type=cst.AgentTypes.pedestrian.name, measures=agent_measures))

    def remove_one_agent(self) -> None:
        """
        Remove one agent from the crowd.

        This method removes the last agent from the list of agents if the list is not empty.
        """

        if self.agents:
            self.agents.pop()

    def create_agents(self, number_agents: float) -> None:
        """
        Create a specified number of agents in the crowd.

        Parameters:
            number_agents (float): The number of agents to create. This will be
                                   converted to an integer.

        Returns:
            None
        """

        for _ in range(int(number_agents)):
            self.add_one_agent()

    def get_crowd_measures(self) -> dict[str, float]:
        """
        Get the crowd statistics.

        This method calculates various statistics for the crowd, including the number of agents of each type,
        and statistical measures (mean, standard deviation, minimum, and maximum) for different parts of the agents.

        Returns:
            dict[str, float]: A dictionary containing the crowd statistics. The keys are:
                - "num_<AgentType>": Number of agents of each type (e.g., "num_Pedestrian", "num_Bike").
                - "<PartName>_mean": Mean value of the measure for the given part.
                - "<PartName>_std_dev": Standard deviation of the measure for the given part.
                - "<PartName>_min": Minimum value of the measure for the given part.
                - "<PartName>_max": Maximum value of the measure for the given part.
        """

        crowd_measures = {}

        # Loop over the enumeration of AgentTypes to get the number of pedestrians and bikes
        for agent_type in cst.AgentTypes:
            count = sum(1 for agent in self.agents if agent.agent_type == agent_type.name)
            crowd_measures[f"num_{agent_type.name}"] = count

        # Loop over PedestrianParts and BikeParts to get statistics for each measure
        for parts_enum in [cst.PedestrianParts, cst.BikeParts]:
            for part in parts_enum:
                measures = [agent.measures.__dict__[part.name] for agent in self.agents if hasattr(agent.measures, part.name)]
                if measures:
                    crowd_measures[f"{part.name}_mean"] = sum(measures) / len(measures)
                    crowd_measures[f"{part.name}_std_dev"] = (
                        sum((x - crowd_measures[f"{part.name}_mean"]) ** 2 for x in measures) / (len(measures) - 1)
                    ) ** 0.5
                    crowd_measures[f"{part.name}_min"] = min(measures)
                    crowd_measures[f"{part.name}_max"] = max(measures)

        return crowd_measures

    def get_agents_params(self) -> list[dict[str, float]]:
        """
        Get the parameters of each agent in the crowd.

        Returns:
            list[dict[str, float]]: A list of dictionaries where each dictionary contains
            the parameters of an agent. The keys in the dictionary are:
                - "agent_type": The type of the agent.
                - "shapes": Additional parameters of the agent's shapes.
        """

        crowd_dict = {
            f"agent{id_agent}": {
                "agent_type": agent.agent_type,
                "shapes": agent.shapes2D.get_additional_parameters(),
            }
            for id_agent, agent in enumerate(self.agents)
        }

        return crowd_dict

    def calculate_interpenetration(self, with_inflation: bool = False) -> float:
        """
        Calculate the interpenetration area between pedestrians.

        This method calculates the total area of interpenetration between the geometric shapes of pedestrians
        in the crowd. Optionally, the geometric shapes can be inflated by a buffer before calculating the
        interpenetration.

        Parameters:
            with_inflation (bool): If True, inflate the geometric shapes by a buffer of 5.0 units before
                       calculating the interpenetration. Default is False.

        Returns:
            float: The total interpenetration area between pedestrians and between pedestrians and boundaries.
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
        """
        Compute the convex hull area of the crowd.

        This method calculates the area of the convex hull that encompasses all the agents in the crowd.
        It collects the exterior coordinates of the 2D shapes of all agents, computes the convex hull
        of these points, and returns the area of the convex hull.

        Returns:
            float: The area of the convex hull surrounding the crowd.
        """

        points = []
        for agent in self.agents:
            points.extend(agent.shapes2D.get_geometric_shape().exterior.coords[:-1])
        hull = ConvexHull(points)

        return hull.area

    def compute_energy(self) -> float:
        """
        Compute the energy of the crowd.

        The energy is calculated as a weighted sum of the interpenetration and the convex hull area of the crowd.
        The interpenetration is scaled by a factor of 100, and the convex hull area is scaled by a factor of 0.1.

        Returns:
            float: The computed energy of the crowd.
        """

        interpenetration = self.calculate_interpenetration(with_inflation=True)
        convex_hull_area = self.compute_crowd_convex_hull_area()

        return 100.0 * interpenetration + convex_hull_area / 10.0

    def pack_agents_MCMC(self) -> float:
        """
        Run an MCMC algorithm to pack the agents of the crowd.

        This method iteratively attempts to move and rotate agents in the crowd
        to minimize the overall energy of the system. It uses a Monte Carlo
        Markov Chain (MCMC) approach to explore the state space of possible
        configurations.

        Returns:
            float: The final energy of the system after attempting to pack the agents.
        """

        current_energy = self.compute_energy()
        cpt_rejected = 0

        # Perform a number of iterations to pack the agents
        for _ in range(cst.MAX_NB_ITERATIONS):
            # Choose a random agent
            agent = np.random.choice(self.agents)

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
    def calculate_contact_force(agent_centroid: np.ndarray, other_centroid: np.ndarray) -> np.ndarray:
        """
        Calculate the repulsive force between two centroids.

        Parameters:
            agent_centroid (np.ndarray): The centroid of the agent.
            other_centroid (np.ndarray): The centroid of the other agent.

        Returns:
            np.ndarray: The normalized direction of the repulsive force. If the centroids coincide, a small random force is returned.
        """

        delta = agent_centroid - other_centroid
        norm_delta = np.linalg.norm(delta)
        if norm_delta != 0:
            return delta / norm_delta  # Direction of the force
        return np.random.rand(2)  # Small random force if centroids coincide

    # the repulsive force should exponentially decrease with the distance between the two agents
    @staticmethod
    def calculate_repulsive_force(agent_centroid: np.ndarray, other_centroid: np.ndarray) -> np.ndarray:
        """Calculate the repulsive force between two centroids, exponentially decreasing with distance."""
        delta = agent_centroid - other_centroid
        norm_delta = np.linalg.norm(delta)
        if norm_delta == 0:
            return np.random.rand(2)  # Small random force if centroids coincide
        direction = delta / norm_delta  # direction of the force
        # Calculate the magnitude of the repulsive force, exponentially decreasing with distance
        force_magnitude = np.exp(-cst.DEFAULT_DECAY_REPULSION_RATE * norm_delta)
        # TODO : voir comment on peut modifier ce decay depuis streamlit
        # Return the repulsive force vector
        return force_magnitude * direction

    @staticmethod
    def calculate_rotational_force() -> float:
        """Calculate a rotational force based on the agent's current orientation."""
        return np.random.uniform(-10.0, 10.0)  # Random rotational force between -10 and 10 degrees

    def pack_agents_with_forces(self) -> None:
        # TODO : améliroer la rapidité
        """Simulates the application of forces on agents within a polygonal cell over a number of iterations."""
        Temperature = 1.0
        for _ in range(cst.MAX_NB_ITERATIONS):
            # Check for overlaps and apply forces if necessary
            for i_agent, current_agent in enumerate(self.agents):
                force = np.array([0.0, 0.0])
                rotational_force = 0.0
                current_geometric = current_agent.shapes2D.get_geometric_shape()
                current_centroid = np.array(current_geometric.centroid.coords[0])
                # Calculate repulsive force between agents
                for j_agent, neigh_agent in enumerate(self.agents):
                    neigh_geometric = neigh_agent.shapes2D.get_geometric_shape()
                    if i_agent != j_agent:
                        neigh_centroid = np.array(neigh_geometric.centroid.coords[0])
                        force += Crowd.calculate_repulsive_force(current_centroid, neigh_centroid)
                        if current_geometric.intersects(neigh_geometric):
                            force += Crowd.calculate_contact_force(current_centroid, neigh_centroid)
                            rotational_force += Crowd.calculate_rotational_force() * Temperature

                # TODO : add a posibility to remove wall interaction
                # Calculate repulsive force between agent and wall
                # if not self.boundaries.contains(current_geometric):
                #     nearest_point = np.array(
                #         self.boundaries.exterior.interpolate(self.boundaries.exterior.project(current_geometric.centroid)).coords[
                #             0
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
