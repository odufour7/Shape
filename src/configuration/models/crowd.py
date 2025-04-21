"""Module containing the Crowd class, which represents a crowd of pedestrians in a room."""

import numpy as np
from numpy.typing import NDArray
from shapely.geometry import Point, Polygon

import configuration.utils.constants as cst
from configuration.models.agents import Agent
from configuration.models.measures import CrowdMeasures, create_pedestrian_measures, draw_agent_measures, draw_agent_type
from configuration.models.shapes2D import Shapes2D
from configuration.utils.typing_custom import DynamicCrowdDataType, GeometryDataType, StaticCrowdDataType


class Crowd:
    """
    Class representing a crowd of pedestrians in a room.

    Parameters
    ----------
    measures : dict[str, float] | CrowdMeasures | None
        Crowd measures data. Can be:
            - A dictionary of agent statistics (str keys, float values)
            - A CrowdMeasures instance
            - None (default) when agents are provided instead
    agents : list[Agent] | None
        List of Agent instances. If None, measures must be provided.
        When agents are provided, crowd statistics will be calculated from them.
    boundaries : Polygon | None
        A shapely Polygon instance defining the boundaries.
        If None, a default large square boundary is created.
    """

    def __init__(
        self,
        measures: dict[str, float] | CrowdMeasures | None = None,
        agents: list[Agent] | None = None,
        boundaries: Polygon | None = None,
    ) -> None:
        """
        Initialize the class instance with measures, agents, and boundaries.

        Parameters
        ----------
        measures : dict[str, float] | CrowdMeasures | None
            Crowd measures data. Can be:
                - A dictionary of agent statistics (str keys, float values)
                - A CrowdMeasures instance
                - None (default) when agents are provided instead
        agents : list[Agent] | None
            List of Agent instances. If None, measures must be provided or default will be used.
            When agents are provided, crowd statistics will be calculated from them.
        boundaries : Polygon | None
            A shapely Polygon instance defining the boundaries.
            If None, a default large square boundary is created.

        Raises
        ------
        ValueError
            If both measures and agents are provided,
            or if the provided arguments are of incorrect types.
        """
        # Only allow one of: (measures is not None and agents is None), (measures is None and agents is not None),
        # or (measures is None and agents is None)
        if measures is not None and agents is not None:
            raise ValueError("You must provide only one of 'measures' or 'agents', or neither (not both).")

        # Boundaries validation
        if boundaries is None:
            boundaries = Polygon()
        elif not isinstance(boundaries, Polygon):
            raise ValueError("'boundaries' should be a shapely Polygon instance even if empty")

        # If agents are provided (measures must be None)
        if agents is not None:
            if not isinstance(agents, list):
                raise ValueError("'agents' should be a list of Agent instances")
            if agents and not all(isinstance(agent, Agent) for agent in agents):
                raise ValueError("All elements in 'agents' must be Agent instances")
            self._agents = agents
            # Calculate measures from agents
            self._measures = CrowdMeasures(agent_statistics=self.get_crowd_statistics())
        # If measures are provided (agents must be None)
        elif measures is not None:
            if isinstance(measures, CrowdMeasures):
                self._measures = measures
            elif isinstance(measures, dict):
                if not measures:
                    self._measures = CrowdMeasures()
                elif all(isinstance(k, str) and isinstance(v, (int, float)) for k, v in measures.items()):
                    self._measures = CrowdMeasures(agent_statistics=measures)
                else:
                    raise ValueError("If 'measures' is a dictionary, it must have string keys and numeric values")
            else:
                raise ValueError("'measures' should be None, a dict[str, float] or a CrowdMeasures instance")
            self._agents = []
        # If both are None, use defaults
        else:
            self._measures = CrowdMeasures()
            self._agents = []

        self._boundaries = boundaries

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
            A list of Agent instances.

        Raises
        ------
        ValueError
            If `value` is not a list or if any element in `value` is not an instance of Agent.
        """
        if not isinstance(value, list) or not all(isinstance(agent, Agent) for agent in value):
            raise ValueError("'agents' should be a list of Agent instances")
        self._agents = value
        self._measures.agent_statistics = self.get_crowd_statistics()

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
        if self.measures.agent_statistics:
            drawn_agent_type = draw_agent_type(self.measures)
            drawn_agent_measures = draw_agent_measures(drawn_agent_type, self.measures)
            self.agents.append(Agent(agent_type=drawn_agent_type, measures=drawn_agent_measures))

        # Case 3: Use the default ANSURII database if no other data is available
        elif not self.measures.agent_statistics:
            drawn_agent = np.random.choice(np.array(list(self.measures.default_database.values()), dtype="object"))
            agent_measures = create_pedestrian_measures(drawn_agent)
            self.agents.append(Agent(agent_type=cst.AgentTypes.pedestrian, measures=agent_measures))

    def create_agents(self, number_agents: int = cst.DEFAULT_AGENT_NUMBER) -> None:
        """
        Create multiple agents in the crowd from the given CrowdMeasures (ANSURII database by default).

        Parameters
        ----------
        number_agents : int
            Number of agents to create.
        """
        for _ in range(number_agents):
            self.add_one_agent()

    def calculate_interpenetration(self) -> tuple[float, float]:
        """
        Compute the total interpenetration area between pedestrians and between pedestrians and boundaries.

        Returns
        -------
        float
            The total interpenetration area between pedestrians and between pedestrians and boundaries.
        """
        interpenetration_between_agents = 0.0
        interpenetration_with_boundaries = 0.0
        n_agents = self.get_number_agents()

        # Loop over all agents in the crowd
        for i_agent, current_agent in enumerate(self.agents):
            current_geometric = current_agent.shapes2D.get_geometric_shape()
            # Loop over all other agents in the crowd
            for j in range(i_agent + 1, n_agents):
                neigh_agent = self.agents[j]
                neigh_geometric = neigh_agent.shapes2D.get_geometric_shape()
                # Compute interpenetration between current agent and neighbor
                interpenetration_between_agents += current_geometric.intersection(neigh_geometric).area
            # Compute interpenetration with the boundaries
            interpenetration_with_boundaries += current_geometric.difference(self.boundaries).area

        return interpenetration_between_agents, interpenetration_with_boundaries

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
            return np.array(cst.INTENSITY_TRANSLATIONAL_FORCE * delta / norm_delta)  # Return normalized direction of the force

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
            Random rotational force in degrees.
        """
        return float(np.random.uniform(-cst.INTENSITY_ROTATIONAL_FORCE, cst.INTENSITY_ROTATIONAL_FORCE, 1)[0])

    def calculate_boundary_forces(self, forces: NDArray[np.float64], current_geo: Polygon, temperature: float) -> NDArray[np.float64]:
        """
        Compute boundary interaction forces for an agent near environment edges.

        Parameters
        ----------
        forces : NDArray[np.float64]
            Current force vector acting on the agent, shape (3,).
            Format: [x_translation, y_translation, rotation].
        current_geo : Polygon
            Shapely Polygon representing the agent's current geometric position.
        temperature : float
            Current cooling system coefficient (0.0-1.0) that scales rotational forces.

        Returns
        -------
        NDArray[np.float64]
            Updated force vector with boundary interactions.

        Notes
        -----
        - Forces are only applied when the agent is outside the boundaries or touching boundary edges.
        - Force calculations:
            1. Contact force: Linear repulsion from nearest boundary point.
            2. Rotational force: Temperature-scaled random torque.
        """
        if self.boundaries.is_empty or self.boundaries.contains(current_geo):
            return forces

        # Compute the nearest point on the agent between the agent and the boundary
        nearest_point = Point(
            self.boundaries.exterior.interpolate(
                self.boundaries.exterior.project(current_geo.centroid),
            ).coords[0]  # Compute projection distance along boundary
        )
        wall_contact_force = Crowd.calculate_contact_force(current_geo.centroid, nearest_point)
        wall_rotational_force = Crowd.calculate_rotational_force() * temperature
        wall_forces: NDArray[np.float64] = np.concatenate((wall_contact_force, np.array([wall_rotational_force])))

        return forces + wall_forces

    @staticmethod
    def check_validity_parameters_agents_packing(repulsion_length: float, desired_direction: float, random_packing: bool) -> None:
        """
        Validate the input parameters for agent packing.

        Parameters
        ----------
        repulsion_length : float
            The repulsion length, which must be a strictly positive float.
        desired_direction : float
            The desired direction, which must be a float.
        random_packing : bool
            A flag indicating whether random packing is enabled, which must be a boolean.
        """
        if not isinstance(repulsion_length, float):
            raise TypeError("`repulsion_length` should be a float.")
        if not isinstance(desired_direction, float):
            raise TypeError("`desired_direction` should be a float.")
        if not isinstance(random_packing, bool):
            raise TypeError("`random_packing` should be a boolean.")
        if repulsion_length <= 0:
            raise ValueError("`repulsion_length` should be a strictly positive float.")

    def pack_agents_with_forces(
        self,
        repulsion_length: float = cst.DEFAULT_REPULSION_LENGTH,
        desired_direction: float = cst.DEFAULT_DESIRED_DIRECTION,
        random_packing: bool = cst.DEFAULT_RANDOM_PACKING,
    ) -> None:
        """
        Simulate crowd dynamics using physics-based forces to resolve agent overlaps.

        Iteratively calculates repulsive forces between agents and boundary constraints,
        while applying rotational adjustments. Implements a temperature-based cooling
        system to gradually reduce movement intensity over iterations.

        Parameters
        ----------
        repulsion_length : float
            Exponential decay coefficient for repulsive forces between agents (in meters).
            Higher values increase the effective range of repulsion.
        desired_direction : float
            Initial orientation angle in degrees for all agents.
        random_packing : bool
            Whether to apply rotational forces during packing. When True, enables
            random angular adjustments based on collision forces.

        Notes
        -----
        - Boundary handling:
            * Uses Shapely Polygon objects for boundary constraints
            * Agents cannot move outside boundary polygons
            * Boundaries are treated as static, non-physical constraints
        - Force calculations:
            1. Agent-agent repulsion (exponential decay with distance)
            2. Contact forces for overlapping agents
            3. Boundary repulsion for agents near edges
            4. Rotational forces (only when random_packing=True)
        """
        Crowd.check_validity_parameters_agents_packing(
            repulsion_length=repulsion_length,
            desired_direction=desired_direction,
            random_packing=random_packing,
        )

        # Initially, all agents have 90° orientation (head facing up), so we need to rotate them to the desired direction
        for current_agent in self.agents:
            current_agent.rotate(desired_direction - 90.0)

        Temperature = 1.0
        for _ in range(cst.MAX_NB_ITERATIONS):
            # Check for overlaps and apply forces if necessary
            for i_agent, current_agent in enumerate(self.agents):
                # Format: [x_translation (cm), y_translation (cm), rotation (degrees)]
                forces: NDArray[np.float64] = np.array([0.0, 0.0, 0.0])
                current_geometric = current_agent.shapes2D.get_geometric_shape()
                current_centroid: Point = current_geometric.centroid

                # Compute repulsive force between agents
                for j_agent, neigh_agent in enumerate(self.agents):
                    if i_agent == j_agent:
                        continue
                    neigh_geometric = neigh_agent.shapes2D.get_geometric_shape()
                    neigh_centroid: Point = neigh_geometric.centroid
                    forces[:-1] += Crowd.calculate_repulsive_force(current_centroid, neigh_centroid, repulsion_length)
                    if current_geometric.intersects(neigh_geometric):
                        forces[:-1] += Crowd.calculate_contact_force(current_centroid, neigh_centroid)
                        forces[-1] += Crowd.calculate_rotational_force() * Temperature

                # Compute repulsive force between agent and wall
                forces = (
                    self.calculate_boundary_forces(forces, current_geometric, Temperature)
                    if not self.boundaries.is_empty and not self.boundaries.contains(current_geometric)
                    else forces
                )

                # Rotate pedestrian
                if random_packing:
                    current_agent.rotate(forces[-1])

                # Translate pedestrian
                new_position = Point(np.array(current_centroid.coords[0], dtype=np.float64) + forces[:-1])
                if self.boundaries.is_empty:
                    current_agent.translate(forces[:-1][0], forces[:-1][1])
                elif self.boundaries.contains(new_position):
                    current_agent.translate(forces[:-1][0], forces[:-1][1])

            # Decrease the temperature at each iteration
            Temperature = max(0.0, Temperature - 0.1)

    def unpack_crowd(self) -> None:
        """Translate all agents in the crowd to the origin (0, 0)."""
        for agent in self.agents:
            current_position: Point = agent.get_position()
            translation_vector = np.array([-current_position.x, -current_position.y])
            agent.translate(*translation_vector)

    @staticmethod
    def compute_stats(data: list[float], stats_key: str) -> float | None:
        """
        Compute statistics for a given data list and stats key.

        Parameters
        ----------
        data : list[float]
            The list of numerical values to compute statistics for.
        stats_key : str
            The type of statistic to compute ('mean', 'std_dev', 'min', 'max').

        Returns
        -------
        float | None
            The computed statistic or None if data is empty or invalid.
        """
        if "mean" in stats_key:
            return float(np.mean(data, dtype=float)) if data else None
        if "std_dev" in stats_key:
            return float(np.std(data, ddof=1, dtype=float)) if len(data) >= 2 else None
        if "min" in stats_key:
            return float(np.min(data)) if data else None
        if "max" in stats_key:
            return float(np.max(data)) if data else None
        raise ValueError(f"Unknown stats key: {stats_key}")

    def get_crowd_statistics(self) -> dict[str, float | int | None]:
        """
        Measure the statistics of the crowd.

        Returns
        -------
        dict[str, float | int | None]
            A dictionary containing the computed statistics for the crowd. The keys are formatted as follows:
                - "{kind}_proportion": Count of agents (e.g., "male_proportion" or "bike_proportion" or "pedestrian_proportion")
                - "{part}_mean": Mean value for each body/bike part measurement
                - "{part}_std_dev": Sample standard deviation for each part
                - "{part}_min": Minimum observed value for each part
                - "{part}_max": Maximum observed value for each part
        """
        # Initialize statistics dictionary
        stats_counts: dict[str, int] = {
            "pedestrian_number": 0,
            "male_number": 0,
            "bike_number": 0,
        }
        stats_lists: dict[str, list[float]] = {
            "pedestrian_weight": [],
            "bike_weight": [],
            "male_bideltoid_breadth": [],
            "male_chest_depth": [],
            "female_bideltoid_breadth": [],
            "female_chest_depth": [],
            "wheel_width": [],
            "total_length": [],
            "handlebar_length": [],
            "top_tube_length": [],
        }

        # Collect data from agents
        for agent in self.agents:
            weight = agent.measures.measures[cst.CommonMeasures.weight.name]
            if agent.agent_type == cst.AgentTypes.pedestrian:
                stats_counts["pedestrian_number"] += 1
                bideltoid_breadth = agent.measures.measures[cst.PedestrianParts.bideltoid_breadth.name]
                chest_depth = agent.measures.measures[cst.PedestrianParts.chest_depth.name]
                if agent.measures.measures["sex"] == "male":
                    stats_counts["male_number"] += 1
                    stats_lists["male_bideltoid_breadth"].append(bideltoid_breadth)
                    stats_lists["male_chest_depth"].append(chest_depth)
                else:
                    stats_lists["female_bideltoid_breadth"].append(bideltoid_breadth)
                    stats_lists["female_chest_depth"].append(chest_depth)

                stats_lists["pedestrian_weight"].append(weight)

            elif agent.agent_type == cst.AgentTypes.bike:
                stats_counts["bike_number"] += 1
                stats_lists["bike_weight"].append(weight)
                stats_lists["wheel_width"].append(agent.measures.measures[cst.BikeParts.wheel_width.name])
                stats_lists["total_length"].append(agent.measures.measures[cst.BikeParts.total_length.name])
                stats_lists["handlebar_length"].append(agent.measures.measures[cst.BikeParts.handlebar_length.name])
                stats_lists["top_tube_length"].append(agent.measures.measures[cst.BikeParts.top_tube_length.name])

        # Compute proportions
        total_agents: int = self.get_number_agents()
        measures: dict[str, float | int | None] = {
            "male_proportion": stats_counts["male_number"] / stats_counts["pedestrian_number"]
            if stats_counts["pedestrian_number"] > 0
            else None,
            "pedestrian_proportion": stats_counts["pedestrian_number"] / total_agents if total_agents > 0 else None,
            "bike_proportion": stats_counts["bike_number"] / total_agents if total_agents > 0 else None,
        }

        # Compute detailed statistics for relevant keys
        for part_key in [
            "pedestrian_weight",
            "bike_weight",
            "male_bideltoid_breadth",
            "male_chest_depth",
            "female_bideltoid_breadth",
            "female_chest_depth",
            "wheel_width",
            "total_length",
            "handlebar_length",
            "top_tube_length",
        ]:
            for stats_key in ["_min", "_max", "_mean", "_std_dev"]:
                measures[part_key + stats_key] = Crowd.compute_stats(stats_lists[part_key], stats_key)

        return measures


def create_agents_from_dynamic_static_geometry_parameters(
    static_dict: StaticCrowdDataType, dynamic_dict: DynamicCrowdDataType, geometry_dict: GeometryDataType
) -> Crowd:
    """
    Create agents from dynamic and static geometry parameters.

    Parameters
    ----------
    static_dict : StaticCrowdDataType
        Dictionary containing static crowd data.
    dynamic_dict : DynamicCrowdDataType
        Dictionary containing dynamic crowd data.
    geometry_dict : GeometryDataType
        Dictionary containing geometry data.

    Returns
    -------
    Crowd
        A Crowd object containing the created agents and the scene boundaries.
    """
    # --- Extract wall polygons and set boundaries ---
    wall_polygons = [
        Polygon(
            [
                [corner["Coordinates"][0] * cst.M_TO_CM, corner["Coordinates"][1] * cst.M_TO_CM]
                for corner in wall_data["Corners"].values()
            ]
        )
        for wall_data in geometry_dict.get("Geometry", {}).get("Wall", {}).values()
    ]
    if not wall_polygons:
        raise ValueError("No wall polygons found in geometry_dict.")
    boundaries: Polygon = max(wall_polygons, key=lambda polygon: polygon.area)  # Set the largest polygon as boundaries

    # --- Extract agent positions and orientations ---
    agent_positions = {agent["Id"]: agent["Kinematics"]["Position"] for agent in dynamic_dict.get("Agents", {}).values()}
    agent_orientations = {agent["Id"]: agent["Kinematics"]["theta"] for agent in dynamic_dict.get("Agents", {}).values()}

    # --- Create agents ---
    all_agents = []
    for agent_data in static_dict.get("Agents", {}).values():
        if agent_data.get("Type") != cst.AgentTypes.pedestrian.name.lower():  # Skip non-pedestrian agents
            continue

        agent_id: int = agent_data["Id"]
        wanted_center_of_mass: tuple[float, float] = agent_positions.get(agent_id, (0.0, 0.0))  # m
        wanted_center_of_mass = np.array(wanted_center_of_mass) * cst.M_TO_CM  # cm
        wanted_orientation: float = np.degrees(agent_orientations.get(agent_id, 0.0))  # radian

        agent_shape2D = Shapes2D(agent_type=cst.AgentTypes.pedestrian)

        for shape_name, shape_data in agent_data.get("Shapes", {}).items():
            # Calculate global position of the shape
            rel_x, rel_y = shape_data["Position"]  # m
            agent_shape2D.add_shape(
                name=shape_name,
                shape_type=cst.ShapeTypes.disk.name,
                material=cst.MaterialNames.human.name,
                radius=shape_data["Radius"] * cst.M_TO_CM,
                x=rel_x * cst.M_TO_CM,
                y=rel_y * cst.M_TO_CM,
            )

        agent_measures = {
            "sex": "male",
            "bideltoid_breadth": agent_shape2D.get_bideltoid_breadth(),
            "chest_depth": agent_shape2D.get_chest_depth(),
            "height": cst.DEFAULT_PEDESTRIAN_HEIGHT,
            "weight": cst.DEFAULT_PEDESTRIAN_WEIGHT,
        }
        new_agent = Agent(agent_type=cst.AgentTypes.pedestrian, measures=agent_measures)
        actual_position = new_agent.get_position()
        actual_orientation = new_agent.get_agent_orientation()
        new_agent.translate(wanted_center_of_mass[0] - actual_position.x, wanted_center_of_mass[1] - actual_position.y)
        new_agent.rotate(wanted_orientation - actual_orientation)
        all_agents.append(new_agent)

    return Crowd(agents=all_agents, boundaries=boundaries)
