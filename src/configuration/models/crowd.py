"""Module containing the Crowd class, which represents a crowd of pedestrians in a room."""

import numpy as np
from numpy.typing import NDArray
from shapely.geometry import Point, Polygon

import configuration.utils.constants as cst
from configuration.models.agents import Agent
from configuration.models.measures import (
    CrowdMeasures,
    create_bike_measures,
    create_pedestrian_measures,
    draw_agent_measures,
    draw_agent_type,
)
from configuration.models.shapes2D import Shapes2D
from configuration.utils.typing_custom import DynamicCrowdDataType, GeometryDataType, StaticCrowdDataType


class Crowd:
    """
    Class representing a crowd of pedestrians in a room.

    Parameters
    ----------
    measures : dict[str, float] | dict[int, dict[str, float]] | CrowdMeasures | None
        Crowd measures data. Can be:
            - A dictionary of agent statistics (str keys, float values)
            - A custom database (int keys, dict values)
            - A CrowdMeasures instance
            - None (default), which creates a default CrowdMeasures object
    agents : list[Agent] | None
        List of Agent instances. If None, an empty list is used.
    boundaries : Polygon | None
        A shapely Polygon instance defining the boundaries.
        If None, a default large square boundary is created.
    """

    def __init__(
        self,
        measures: dict[str, float] | dict[int, dict[str, float]] | CrowdMeasures | None = None,
        agents: list[Agent] | None = None,
        boundaries: Polygon | None = None,
    ) -> None:
        """
        Initialize the class instance with measures, agents, and boundaries.

        Parameters
        ----------
        measures : dict[str, float] | dict[int, dict[str, float]] | CrowdMeasures | None
            Crowd measures data. Can be:
                - A dictionary of agent statistics (str keys, float values)
                - A custom database (int keys, dict values)
                - A CrowdMeasures instance
                - None (default), which creates a default CrowdMeasures object
        agents : list[Agent] | None
            List of Agent instances. If None, an empty list is used.
        boundaries : Polygon | None
            A shapely Polygon instance defining the boundaries.
            If None, a default large square boundary is created.
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
            boundaries = Polygon()
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
            A list of Agent instances.

        Raises
        ------
        ValueError
            If `value` is not a list or if any element in `value` is not an instance of Agent.
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
    def measures(self, value: dict[str, float] | dict[int, dict[str, float]] | CrowdMeasures) -> None:
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

    def create_agents(self, number_agents: int = cst.DEFAULT_AGENT_NUMBER) -> None:
        """
        Create multiple agents in the crowd through repeated additions.

        Parameters
        ----------
        number_agents : int
            Number of agents to create.
        """
        for _ in range(number_agents):
            self.add_one_agent()

    def create_agents_from_dynamic_static_geometry_parameters(
        self, static_dict: StaticCrowdDataType, dynamic_dict: DynamicCrowdDataType, geometry_dict: GeometryDataType
    ) -> None:
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
        self.boundaries = max(wall_polygons, key=lambda polygon: polygon.area)  # Set the largest polygon as boundaries

        # --- Extract agent positions and orientations ---
        agent_positions = {agent["Id"]: agent["Kinematics"]["Position"] for agent in dynamic_dict.get("Agents", {}).values()}
        agent_orientations = {agent["Id"]: agent["Kinematics"]["theta"] for agent in dynamic_dict.get("Agents", {}).values()}

        # --- Create agents ---
        for agent_data in static_dict.get("Agents", {}).values():
            if agent_data.get("Type") != cst.AgentTypes.pedestrian.name.lower():  # Skip non-pedestrian agents
                continue

            agent_id: int = agent_data["Id"]
            center_of_mass: tuple[float, float] = agent_positions.get(agent_id, (0.0, 0.0))  # m
            orientation: float = agent_orientations.get(agent_id, 0.0)  # radian

            agent_shape2D = Shapes2D(agent_type=cst.AgentTypes.pedestrian)

            for shape_name, shape_data in agent_data.get("Shapes", {}).items():
                # Calculate global position of the shape
                rel_x, rel_y = shape_data["Position"]  # m
                x_shape = (center_of_mass[0] + rel_x) * cst.M_TO_CM
                y_shape = (center_of_mass[1] + rel_y) * cst.M_TO_CM
                agent_shape2D.add_shape(
                    name=shape_name,
                    shape_type=cst.ShapeTypes.disk.name,
                    material=cst.MaterialNames.human.name,
                    radius=shape_data["Radius"] * cst.M_TO_CM,
                    x=x_shape,
                    y=y_shape,
                )

            agent_measures = {
                "sex": "male",
                "bideltoid_breadth": agent_shape2D.get_bideltoid_breadth(),
                "chest_depth": agent_shape2D.get_chest_depth(),
                "height": cst.DEFAULT_PEDESTRIAN_HEIGHT,
                "weight": cst.DEFAULT_PEDESTRIAN_WEIGHT,
            }
            new_agent = Agent(agent_type=cst.AgentTypes.pedestrian, measures=agent_measures, shapes2D=agent_shape2D)
            new_agent.rotate(np.degrees(orientation))
            self.agents.append(new_agent)

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
        return np.random.uniform(-20.0, 20.0)

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

    def measure_crowd_statistics(self) -> dict[str, float | int | None]:
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
